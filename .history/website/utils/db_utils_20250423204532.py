from .. import db
from ..models import Recipe, Favorite, RecipeDetail, RecipeIngredient, Ingredient

def get_recipe_by_id(recipe_id):
    """Get a recipe by its ID."""
    return Recipe.query.filter_by(recipe_id=recipe_id).first()

def get_recipes_by_ingredient(ingredient_name):
    """Get recipes that contain a specific ingredient."""
    ingredient = Ingredient.query.filter_by(ingr_name=ingredient_name).first()
    if ingredient:
        return Recipe.query.join(RecipeIngredient).filter(
            RecipeIngredient.ingr_id == ingredient.ingr_id
        ).all()
    return []

def get_recipe_details(recipe_id):
    """Get detailed instructions for a recipe."""
    return RecipeDetail.query.filter_by(recipe_id=recipe_id).order_by(RecipeDetail.step_number).all()

def get_recipe_ingredients(recipe_id):
    """Get all ingredients for a recipe with their quantities and units."""
    return db.session.query(
        Ingredient.ingr_name,
        RecipeIngredient.quantity,
        RecipeIngredient.unit
    ).join(
        RecipeIngredient, Ingredient.ingr_id == RecipeIngredient.ingr_id
    ).filter(
        RecipeIngredient.recipe_id == recipe_id
    ).all()

def get_user_favorites(user_id):
    """Get all favorites for a user."""
    return Recipe.query.join(Favorite).filter(Favorite.user_id == user_id).all()

def add_favorite(user_id, recipe_id):
    """Add a recipe to user's favorites."""
    existing = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if not existing:
        favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.commit()
        return favorite
    return existing

def remove_favorite(user_id, recipe_id):
    """Remove a recipe from user's favorites."""
    favorite = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return True
    return False
