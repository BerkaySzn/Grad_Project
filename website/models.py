from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Many-to-many relationship with Recipe
    recipes = db.relationship('RecipeIngredient', backref='ingredient', lazy=True)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    prep_time = db.Column(db.Integer)  # in minutes
    cook_time = db.Column(db.Integer)  # in minutes
    image_url = db.Column(db.String(300))
    # Many-to-many relationship with Ingredient
    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True)
    favorites = db.relationship('Favorite', backref='recipe', lazy=True)

class RecipeIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantity = db.Column(db.String(50))
    unit = db.Column(db.String(50))

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())
