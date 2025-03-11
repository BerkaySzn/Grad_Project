from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file, session
from flask_login import login_required, current_user
from .models import Recipe, Ingredient, Favorite
from . import db
import json
import os
from werkzeug.utils import secure_filename
from PIL import Image
import io
from .utils.object_detection import ObjectDetector
import pyodbc

views = Blueprint('views', __name__)
detector = ObjectDetector()  # Initialize the YOLO model

# Map class IDs to ingredient names
INGREDIENT_MAP = {
    1: "apple",
    2: "orange"
}

# Add connection string at the top with other imports
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-OPP7BQ4\\MSSQLSERVER01;DATABASE=Grad_Project_DB;"
    "Trusted_Connection=yes;TrustServerCertificate=yes;"
)

@views.route('/', methods=['GET'])
def home():
    return render_template("home.html", user=current_user)

@views.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            # Read the image file
            image_bytes = file.read()
            
            # Detect ingredients
            try:
                detections = detector.detect_ingredients(image_bytes)
                print(f"Detections: {detections}")
                
                # Convert detections to the format expected by your code
                class_ids_list = [int(d['class']) for d in detections]
                
            except Exception as e:
                print(f"Error in detect_ingredients: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return jsonify({'error': f'Error detecting ingredients: {str(e)}'}), 500
            
            # Get annotated image
            try:
                annotated_image = detector.detect_and_draw(image_bytes)
                print("Annotated image received")
            except Exception as e:
                print(f"Error in detect_and_draw: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return jsonify({'error': f'Error creating annotated image: {str(e)}'}), 500
            
            # Process the detected class IDs to map them to ingredient names
            detected_ingredients = []
            for class_id in class_ids_list:
                if class_id in INGREDIENT_MAP:
                    detected_ingredients.append({
                        'name': INGREDIENT_MAP[class_id],
                        'confidence': next((d['confidence'] for d in detections if d['class'] == class_id), 0.0),
                        'bbox': next((d['bbox'] for d in detections if d['class'] == class_id), [])
                    })
            
            if not detected_ingredients:
                return jsonify({'error': 'No ingredients detected'}), 400
            
            # Store detected ingredients in session
            session['detected_ingredients'] = [ing['name'] for ing in detected_ingredients]
            
            # Return the results
            return jsonify({
                'success': True,
                'ingredients': detected_ingredients,
                'annotated_image': annotated_image.decode('latin1')
            })
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid image file'}), 400

def find_recipes_by_ingredients(ingredients):
    """Find recipes based on detected ingredients."""
    try:
        print(f"Searching for recipes with ingredients: {ingredients}")
        
        # First, let's verify the database connection and table structure
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            
            # Check if RECIPES table exists
            try:
                cursor.execute("SELECT TOP 1 * FROM RECIPES")
                columns = [column[0] for column in cursor.description]
                print(f"Found RECIPES table with columns: {columns}")
            except Exception as e:
                print(f"Error accessing RECIPES table: {e}")
                # Create the table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE RECIPES (
                        Recipes_ID INT PRIMARY KEY IDENTITY(1,1),
                        Recipes_Name NVARCHAR(255),
                        Ingredients NVARCHAR(MAX),
                        Instructions NVARCHAR(MAX),
                        Prep_Time INT,
                        Cook_Time INT,
                        Image_URL NVARCHAR(500),
                        Ingredients_Type INT
                    )
                """)
                print("Created RECIPES table")
                
                # Insert sample recipes
                cursor.execute("""
                    INSERT INTO RECIPES (Recipes_Name, Ingredients, Instructions, Prep_Time, Cook_Time, Image_URL, Ingredients_Type)
                    VALUES 
                    ('Apple Pie', 'apple,sugar,flour', 'Mix ingredients and bake', 15, 30, '/static/img/apple-pie.jpg', 1),
                    ('Orange Juice', 'orange,water', 'Squeeze oranges and mix with water', 5, 0, '/static/img/orange-juice.jpg', 2)
                """)
                conn.commit()
                print("Inserted sample recipes")
            
            # Now proceed with the recipe search
            ingredient_types = []
            for ingredient in ingredients:
                print(f"Looking for type ID for ingredient: {ingredient}")
                for type_id, name in INGREDIENT_MAP.items():
                    if name.lower() == ingredient.lower():
                        ingredient_types.append(type_id)
                        print(f"Found type ID {type_id} for {ingredient}")
            
            if not ingredient_types:
                print("No valid ingredient types found in INGREDIENT_MAP")
                print(f"Available ingredients in map: {INGREDIENT_MAP}")
                return []

            # Convert the list to a tuple for SQL query
            types_tuple = tuple(ingredient_types)
            print(f"Ingredient type IDs to search for: {types_tuple}")
            
            # Construct the query to find recipes that use ANY of the detected ingredients
            if len(types_tuple) == 1:
                query = f"""
                    SELECT 
                        r.Recipes_ID,
                        r.Recipes_Name,
                        r.Ingredients,
                        r.Instructions,
                        r.Prep_Time,
                        r.Cook_Time,
                        r.Image_URL
                    FROM RECIPES r
                    WHERE r.Ingredients_Type = {types_tuple[0]}
                """
            else:
                query = f"""
                    SELECT 
                        r.Recipes_ID,
                        r.Recipes_Name,
                        r.Ingredients,
                        r.Instructions,
                        r.Prep_Time,
                        r.Cook_Time,
                        r.Image_URL
                    FROM RECIPES r
                    WHERE r.Ingredients_Type IN {types_tuple}
                """

            print(f"Executing SQL query: {query}")
            cursor.execute(query)
            rows = cursor.fetchall()
            print(f"Query returned {len(rows)} recipes")

            if not rows:
                print("No recipes found in database matching the ingredients")
                return []

            # Convert the database results to the expected format
            recipes = []
            for row in rows:
                recipe = {
                    'id': row[0],
                    'name': row[1],
                    'ingredients': row[2].split(',') if row[2] else [],
                    'instructions': row[3] if row[3] else 'Instructions will be added later',
                    'prep_time': row[4] if row[4] else 15,
                    'cook_time': row[5] if row[5] else 30,
                    'image_url': row[6] if row[6] else '/static/img/default-recipe.jpg'
                }
                recipes.append(recipe)
                print(f"Added recipe: {recipe['name']} with ingredients: {recipe['ingredients']}")

            return recipes

    except Exception as e:
        print(f"Error fetching recipes: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []

@views.route('/favorites', methods=['GET'])
@login_required
def favorites():
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    favorite_recipes = [favorite.recipe for favorite in user_favorites]
    
    return render_template("favorites.html", user=current_user, recipes=favorite_recipes)

@views.route('/add-favorite/<int:recipe_id>', methods=['POST'])
@login_required
def add_favorite(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    
    if not recipe:
        flash('Recipe not found.', category='error')
        return redirect(url_for('views.home'))
    
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user.id, recipe_id=recipe_id).first()
    
    if existing_favorite:
        flash('Recipe already in favorites.', category='info')
    else:
        new_favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(new_favorite)
        db.session.commit()
        flash('Recipe added to favorites!', category='success')
    
    return redirect(url_for('views.favorites'))

@views.route('/remove-favorite/<int:recipe_id>', methods=['POST'])
@login_required
def remove_favorite(recipe_id):
    favorite = Favorite.query.filter_by(
        user_id=current_user.id, recipe_id=recipe_id).first()
    
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash('Recipe removed from favorites.', category='success')
    else:
        flash('Recipe not in favorites.', category='error')
    
    return redirect(url_for('views.favorites'))

@views.route('/recipes')
def recipes():
    # Get the detected ingredients from session
    detected_ingredients = session.get('detected_ingredients', [])
    if not detected_ingredients:
        flash('No ingredients detected. Please upload an image first.', 'error')
        return redirect(url_for('views.home'))
    
    recipes = find_recipes_by_ingredients(detected_ingredients)
    return render_template('recipe_results.html', user=current_user, ingredients=detected_ingredients, recipes=recipes)

@views.route('/all-ingredients')
def all_ingredients():
    # Get the detected ingredients from session
    ingredients = session.get('detected_ingredients', [])
    return render_template('all_ingredients.html', ingredients=ingredients)

@views.route('/add-ingredient', methods=['POST'])
def add_ingredient():
    try:
        data = request.get_json()
        ingredient = data.get('ingredient')
        
        if not ingredient:
            return jsonify({'success': False, 'error': 'No ingredient specified'}), 400
            
        # Get current ingredients from session
        current_ingredients = session.get('detected_ingredients', [])
        
        # Add new ingredient if it's not already in the list
        if ingredient not in current_ingredients:
            current_ingredients.append(ingredient)
            session['detected_ingredients'] = current_ingredients
            
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error adding ingredient: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500 