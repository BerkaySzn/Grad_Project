from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    __tablename__ = "Users"
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)
    favorites = db.relationship("Favorite", backref="user", lazy=True)

    # Required for Flask-Login
    @property
    def id(self):
        return self.user_id


class Recipe(db.Model):
    __tablename__ = "Recipes"  # Using the newer Recipes table, not RECIPES
    recipe_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255))
    time = db.Column(db.Integer, nullable=False)
    servings = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    ranking = db.Column(db.Float)

    recipe_details = db.relationship(
        "RecipeDetail", backref="recipe", lazy=True)
    recipe_ingredients = db.relationship(
        "RecipeIngredient", backref="recipe", lazy=True
    )
    favorites = db.relationship("Favorite", backref="recipe", lazy=True)


class Ingredient(db.Model):
    __tablename__ = "Ingredients"
    ingr_id = db.Column(db.Integer, primary_key=True)
    ingr_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255))

    recipe_ingredients = db.relationship(
        "RecipeIngredient", backref="ingredient", lazy=True
    )


class RecipeIngredient(db.Model):
    __tablename__ = "Recipe_Ingredient"
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("Recipes.recipe_id"), primary_key=True
    )
    ingr_id = db.Column(
        db.Integer, db.ForeignKey("Ingredients.ingr_id"), primary_key=True
    )
    quantity = db.Column(db.String(255))
    unit = db.Column(db.String(255))


class RecipeDetail(db.Model):
    __tablename__ = "Recipe_Details"
    detail_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("Recipes.recipe_id"), nullable=False
    )
    step_number = db.Column(db.Integer, nullable=False)
    instruction_text = db.Column(db.String(255), nullable=False)


class Favorite(db.Model):
    __tablename__ = "Favorites"
    user_id = db.Column(db.Integer, db.ForeignKey(
        "Users.user_id"), primary_key=True)
    recipe_id = db.Column(
        db.Integer, db.ForeignKey("Recipes.recipe_id"), primary_key=True
    )
