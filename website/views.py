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

views = Blueprint('views', __name__)
detector = ObjectDetector()  # Initialize the YOLO model

# Map class IDs to ingredient names
INGREDIENT_MAP = {
    0: "tomato",
    1: "onion",
    2: "garlic",
    3: "potato",
    4: "carrot",
    # Add all your class IDs and their corresponding ingredient names here
}

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)

@views.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        flash('No image uploaded', 'error')
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        flash('No image selected', 'error')
        return jsonify({'error': 'No image selected'}), 400
    
    if file:
        # Read the image file
        image_bytes = file.read()
        
        try:
            # Detect ingredients
            detections = detector.detect_ingredients(image_bytes)
            
            # Get annotated image
            annotated_image = detector.detect_and_draw(image_bytes)
            
            # Filter detections with confidence > 0.5 and map class IDs to names
            ingredients = []
            for detection in detections:
                if detection['confidence'] > 0.5:
                    class_id = int(detection['class'])
                    if class_id in INGREDIENT_MAP:
                        ingredients.append({
                            'name': INGREDIENT_MAP[class_id],
                            'confidence': detection['confidence'],
                            'bbox': detection['bbox']
                        })
            
            if not ingredients:
                flash('No ingredients detected in the image', 'error')
                return jsonify({'error': 'No ingredients detected'}), 400
            
            # Find recipes that match these ingredients
            recipes = find_recipes_by_ingredients([ing['name'] for ing in ingredients])
            
            # Return the results
            return jsonify({
                'success': True,
                'ingredients': ingredients,
                'recipes': recipes,
                'annotated_image': annotated_image.decode('latin1')
            })
            
        except Exception as e:
            flash('Error processing image', 'error')
            return jsonify({'error': str(e)}), 500
    
    flash('Invalid image file', 'error')
    return jsonify({'error': 'Invalid image file'}), 400

def find_recipes_by_ingredients(ingredients):
    # This is a placeholder function
    # In a real implementation, you would query the database to find recipes
    # that contain the identified ingredients
    
    # For now, return some dummy recipes
    dummy_recipes = [
        {
            'id': 1,
            'name': 'Tomato Soup',
            'ingredients': ['tomato', 'onion', 'garlic', 'basil'],
            'instructions': 'Cook tomatoes, onions, and garlic. Blend and season.',
            'prep_time': 10,
            'cook_time': 20,
            'image_url': 'https://example.com/tomato_soup.jpg'
        },
        {
            'id': 2,
            'name': 'Pasta Sauce',
            'ingredients': ['tomato', 'onion', 'garlic', 'oregano'],
            'instructions': 'Sauté onions and garlic. Add tomatoes and simmer.',
            'prep_time': 5,
            'cook_time': 30,
            'image_url': 'https://example.com/pasta_sauce.jpg'
        }
    ]
    
    return dummy_recipes

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