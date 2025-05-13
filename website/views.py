from sqlalchemy import text
from flask import request, jsonify, session
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    jsonify,
    redirect,
    url_for,
    send_file,
    session,
)
from flask_login import login_required, current_user
from .models import Recipe, Ingredient, Favorite, RecipeIngredient, RecipeRating
from . import db
from .utils.db_utils import (
    get_recipe_by_id,
    get_recipes_by_ingredient,
    get_recipe_with_details,
    add_favorite,
    remove_favorite,
    get_user_favorites,
)
import json
import os
from werkzeug.utils import secure_filename
from PIL import Image
import io
from .utils.object_detection import ObjectDetector
from sqlalchemy import func

views = Blueprint("views", __name__)
detector = ObjectDetector()

# Map YOLO class IDs to ingredient names
INGREDIENT_MAP = {
    0: 'banana',
    1: 'apple',
    2: 'orange',
    3: 'carrot',
    4: 'lemon',
    5: 'potato',
    6: 'onion',
    7: 'garlic',
    8: 'bell-pepper',
    9: 'tomato',
    10: 'lettuce',
    11: 'spinach',
    12: 'corn',
    13: 'eggplant',
    14: 'cauliflower',
    15: 'cabbage',
    16: 'cucumber',
    17: 'broccoli',
    18: 'pepper',
    19: 'pumpkin',
    20: 'green-bean',
    21: 'peas',
}

UPLOAD_FOLDER = 'website/static/recipe_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route("/", methods=["GET"])
def home():
    return render_template("home.html", user=current_user)


@views.route("/upload-image", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            image_bytes = file.read()
            detections, counts = detector.detect_ingredients(image_bytes)

            detected_ingredients = []

            for d in detections:
                class_id = d["class"]
                if class_id in INGREDIENT_MAP:
                    detected_ingredients.append(
                        {"name": INGREDIENT_MAP[class_id],
                            "count": counts[class_id]}
                    )

            if not detected_ingredients:
                return jsonify({"error": "No ingredients detected"}), 400

            formatted_ingredients = []
            ingredient_counts = {}

            for item in detected_ingredients:
                name = item["name"]
                count = item["count"]
                if name in ingredient_counts:
                    ingredient_counts[name] += count
                else:
                    ingredient_counts[name] = count

            for name, count in ingredient_counts.items():
                formatted_ingredients.append({"name": name})

            session["detected_ingredients"] = formatted_ingredients
            return jsonify(
                {
                    "success": True,
                    "ingredients": formatted_ingredients
                }
            )

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid image file"}), 400


def find_recipes_by_ingredients(ingredients):
    """Find recipes based on detected ingredients."""
    try:
        # Clean up ingredient names (remove count suffixes like 'x1', 'x2')
        cleaned_ingredients = []
        for ingredient in ingredients:
            if isinstance(ingredient, dict) and 'name' in ingredient:
                # Extract just the ingredient name without the count
                name = ingredient['name'].split(' x')[0]
                cleaned_ingredients.append(name)
            elif isinstance(ingredient, str):
                name = ingredient.split(' x')[0]
                cleaned_ingredients.append(name)

        print(f"Searching for recipes with ingredients: {cleaned_ingredients}")

        # Convert list of ingredients to comma-separated string of quoted names
        ingredient_names = ", ".join(
            f"'{ingredient}'" for ingredient in cleaned_ingredients)

        query = f"""
        WITH UserIngredients AS (
            SELECT ingr_id 
            FROM dbo.Ingredients 
            WHERE ingr_name IN ({ingredient_names})
        )
        SELECT r.recipe_id, r.name, COUNT(ri.ingr_id) AS match_count, r.time, r.calories
        FROM dbo.Recipes r
        JOIN dbo.Recipe_Ingredient ri ON r.recipe_id = ri.recipe_id
        JOIN UserIngredients ui ON ri.ingr_id = ui.ingr_id
        GROUP BY r.recipe_id, r.name, r.time, r.calories
        ORDER BY match_count DESC, r.time ASC, r.calories ASC;
        """

        result = db.session.execute(text(query)).fetchall()
        recipe_list = []

        for row in result:
            recipe_list.append({
                "recipe_id": row.recipe_id,
                "name": row.name,
                "match_count": row.match_count,
                "time": row.time,
                "calories": row.calories,
            })

        print(f"Found {len(recipe_list)} unique recipes")
        return recipe_list

    except Exception as e:
        print(f"Error fetching recipes: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []


@views.route("/favorites", methods=["GET"])
@login_required
def favorites():
    favorite_recipes = get_user_favorites(current_user.user_id)
    recipes_with_details = [
        get_recipe_with_details(recipe.recipe_id) for recipe in favorite_recipes
    ]
    return render_template(
        "favorites.html", user=current_user, recipes=recipes_with_details
    )


@views.route("/add-favorite/<int:recipe_id>", methods=["POST"])
@login_required
def add_favorite_route(recipe_id):
    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        flash("Recipe not found.", category="error")
        return redirect(url_for("views.home"))

    add_favorite(current_user.user_id, recipe_id)
    flash("Recipe added to favorites!", category="success")
    return redirect(url_for("views.favorites"))


@views.route("/remove-favorite/<int:recipe_id>", methods=["POST"])
@login_required
def remove_favorite_route(recipe_id):
    if remove_favorite(current_user.user_id, recipe_id):
        flash("Recipe removed from favorites.", category="success")
    else:
        flash("Recipe not in favorites.", category="error")

    return redirect(url_for("views.favorites"))


@views.route("/recipes", methods=["GET"])
@login_required
def recipes():
    detected_ingredients = session.get("detected_ingredients", [])

    if not detected_ingredients:
        flash("No ingredients detected. Please upload an image first.", "error")
        return redirect(url_for("views.home"))

    # Clean ingredient names (remove ' x1' etc.)
    cleaned_names = [i["name"].split(" x")[0]
                     for i in detected_ingredients if "name" in i]

    # Get ingredient IDs from names
    ingredient_objs = Ingredient.query.filter(
        Ingredient.ingr_name.in_(cleaned_names)).all()
    ingredient_ids = [i.ingr_id for i in ingredient_objs]

    # 1. Favoriler içinde eşleşen tarifler
    favorite_recipes = db.session.query(Recipe).join(Favorite).filter(
        Favorite.user_id == current_user.user_id,
        Recipe.recipe_ingredients.any(
            RecipeIngredient.ingr_id.in_(ingredient_ids))
    ).all()

    # 2. Favori olmayan ama eşleşen tarifler (ranking'e göre)
    favorite_ids = [r.recipe_id for r in favorite_recipes]

    non_favorite_recipes = db.session.query(Recipe).filter(
        ~Recipe.recipe_id.in_(favorite_ids),
        Recipe.recipe_ingredients.any(
            RecipeIngredient.ingr_id.in_(ingredient_ids))
    ).order_by(Recipe.ranking.desc()).all()

    # Sonuçları birleştir
    all_recipes = favorite_recipes + non_favorite_recipes

    # Detayları zenginleştir
    recipes_with_details = [get_recipe_with_details(
        r.recipe_id, current_user.user_id) for r in all_recipes]

    return render_template(
        "recipe_results.html",
        user=current_user,
        recipes=recipes_with_details,
        ingredients=ingredient_objs
    )


@views.route("/all-ingredients")
def all_ingredients():
    ingredients = session.get("detected_ingredients", [])
    return render_template("all_ingredients.html", user=current_user, ingredients=ingredients)


@views.route("/add-ingredient", methods=["POST"])
def add_ingredient():
    try:
        data = request.get_json()
        ingredient = data.get("ingredient")

        if not ingredient:
            return jsonify({"success": False, "error": "No ingredient specified"}), 400

        current_ingredients = session.get("detected_ingredients", [])

        if ingredient not in current_ingredients:
            current_ingredients.append(ingredient)
            session["detected_ingredients"] = current_ingredients

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error adding ingredient: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@views.route("/get-recipe-details/<int:recipe_id>", methods=["GET"])
def get_recipe_details_route(recipe_id):
    try:
        user_id = current_user.user_id if current_user.is_authenticated else None
        recipe = get_recipe_with_details(recipe_id, user_id)

        if recipe:
            return jsonify({
                'ingredients': recipe['ingredients'],
                'instructions': recipe['instructions'],
                'ranking': recipe.get('ranking'),
                'is_favorite': recipe.get('is_favorite'),
                'average_rating': recipe.get('average_rating'),
                'user_rating': recipe.get('user_rating'),
                'photo': recipe.get('photo')
            })
        else:
            return jsonify({'error': 'Recipe not found'}), 404
    except Exception as e:
        print(f"Error getting recipe details: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@views.route('/rate-recipe/<int:recipe_id>', methods=['POST'])
@login_required
def rate_recipe(recipe_id):
    rating = int(request.form.get('rating'))
    user_id = current_user.user_id

    # Check if user already rated this recipe
    existing = RecipeRating.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if existing:
        existing.rating = rating
    else:
        new_rating = RecipeRating(user_id=user_id, recipe_id=recipe_id, rating=rating)
        db.session.add(new_rating)
    db.session.commit()
    return jsonify({'success': True})


@views.route('/upload-recipe-photo/<int:recipe_id>', methods=['POST'])
@login_required
def upload_recipe_photo(recipe_id):
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo uploaded'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Create upload folder if it doesn't exist
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            # Secure the filename and create a unique name
            filename = secure_filename(file.filename)
            unique_filename = f"{recipe_id}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Update recipe photo path in database
            recipe = Recipe.query.get(recipe_id)
            if recipe:
                recipe.photo = f"/static/recipe_photos/{unique_filename}"
                db.session.commit()
                return jsonify({'success': True, 'photo_url': recipe.photo})
            else:
                return jsonify({'error': 'Recipe not found'}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400
