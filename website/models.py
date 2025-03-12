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
    __tablename__ = 'RECIPES'
    Recipes_ID = db.Column(db.Integer, primary_key=True)
    Recipes_Name = db.Column(db.String(255), nullable=False)
    Ingredients = db.Column(db.Text)
    Instructions = db.Column(db.Text)
    Prep_Time = db.Column(db.Integer)
    Cook_Time = db.Column(db.Integer)
    Image_URL = db.Column(db.String(500))
    Ingredients_Type = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.Recipes_ID,
            'name': self.Recipes_Name,
            'ingredients': self.Ingredients.split(',') if self.Ingredients else [],
            'instructions': self.Instructions,
            'prep_time': self.Prep_Time,
            'cook_time': self.Cook_Time,
            'image_url': self.Image_URL
        }

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
