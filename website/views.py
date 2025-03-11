from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file
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
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=127.0.0.1\\MSSQLSERVER01;DATABASE=RecipeDatabase;"
    "Trusted_Connection=yes;TrustServerCertificate=yes;"
)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)

@views.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        print("No image in request.files")
        flash('No image uploaded', 'error')
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        print("No selected file")
        flash('No image selected', 'error')
        return jsonify({'error': 'No image selected'}), 400
    
    if file:
        try:
            # Read the image file
            image_bytes = file.read()
            
            # Detect ingredients
            print("Starting ingredient detection...")
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
            print("Getting annotated image...")
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
                print("No ingredients detected")
                flash('No ingredients detected in the image', 'error')
                return jsonify({'error': 'No ingredients detected'}), 400
            
            # Find recipes that match these ingredients
            recipes = find_recipes_by_ingredients([ing['name'] for ing in detected_ingredients])
            print(f"Found {len(recipes)} matching recipes")
            
            # Return the results
            return jsonify({
                'success': True,
                'ingredients': detected_ingredients,
                'recipes': recipes,
                'annotated_image': annotated_image.decode('latin1')
            })
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            flash('Error processing image', 'error')
            return jsonify({'error': str(e)}), 500
    
    flash('Invalid image file', 'error')
    return jsonify({'error': 'Invalid image file'}), 400

def find_recipes_by_ingredients(ingredients):
    """Find recipes based on detected ingredients."""
    try:
        # Convert ingredient names to type IDs based on INGREDIENT_MAP
        ingredient_types = []
        for ingredient in ingredients:
            for type_id, name in INGREDIENT_MAP.items():
                if name == ingredient:
                    ingredient_types.append(type_id)
        
        if not ingredient_types:
            print("No valid ingredient types found")
            return []

        # Convert the list to a tuple for SQL query
        types_tuple = tuple(ingredient_types)
        
        # Construct the query
        if len(types_tuple) == 1:
            query = f"""
                SELECT Recipes_ID, Recipes_Name, Ingredients
                FROM RECIPES
                WHERE Ingredients_Type = {types_tuple[0]}
            """
        else:
            # If you want to handle multiple ingredients in the future
            query = f"""
                SELECT Recipes_ID, Recipes_Name, Ingredients
                FROM RECIPES
                WHERE Ingredients_Type IN {types_tuple}
            """

        print(f"Executing query: {query}")

        # Execute the query
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        if not rows:
            print("No recipes found.")
            return []

        # Convert the database results to the expected format
        recipes = []
        for row in rows:
            recipe = {
                'id': row[0],
                'name': row[1],
                'ingredients': row[2].split(',') if row[2] else [],  # Assuming ingredients are comma-separated
                'instructions': 'Instructions will be added later',  # You can add this column to your database
                'prep_time': 15,  # Default values, you can add these columns to your database
                'cook_time': 30,
                'image_url': 'https://example.com/recipe.jpg'  # You can add this column to your database
            }
            recipes.append(recipe)

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