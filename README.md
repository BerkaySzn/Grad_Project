# Recipe Finder

A web application that identifies ingredients from user-uploaded photos and suggests recipes based on those ingredients.

## Features

- **Ingredient Recognition**: Upload a photo of ingredients and the system will identify them
- **Recipe Suggestions**: Get recipe suggestions based on identified ingredients
- **User Authentication**: Create an account to save your favorite recipes
- **Favorites System**: Save and manage your favorite recipes

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: Microsoft SQL Server with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login
- **Image Processing**: Pillow (Python Imaging Library)

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Update the database connection string in `website/__init__.py` with your MSSQL credentials
6. Run the application:
   ```
   python main.py
   ```
7. Access the application at `http://localhost:5000`

## Project Structure

- `main.py`: Entry point for the application
- `website/`: Main application package
  - `__init__.py`: Flask application factory and configuration
  - `views.py`: Main routes for the application
  - `auth.py`: Authentication routes
  - `models.py`: Database models
  - `templates/`: HTML templates
  - `static/`: Static files (CSS, JavaScript, images)

## Database Schema

- **User**: Stores user information and authentication details
- **Recipe**: Stores recipe information
- **Ingredient**: Stores ingredient information
- **RecipeIngredient**: Many-to-many relationship between recipes and ingredients
- **Favorite**: Stores user's favorite recipes

## Future Enhancements

- Implement actual image recognition for ingredients
- Add more sophisticated recipe matching algorithms
- Allow users to rate and review recipes
- Add social sharing features
- Implement dietary restrictions and preferences
