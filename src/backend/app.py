from flask import Flask, send_from_directory
from .routes import book_routes_bp, book_types_routes_bp, user_routes_bp, loan_routes_bp, user_profiles_routes_bp, cities_routes_bp,categories_routes_bp
from ..database import init_db 
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='library_app_project\src/frontend\static')

# Secret key ONLY FOR DEVELOPMENT. Afterwards it will be stored elsewhere for security
app.config['JWT_SECRET_KEY'] = '5a6520b601d3feb5536ddbd284f77c6ea550b6b1bfc7c2b401c0c4960dcd7e0c'
jwt = JWTManager(app)
CORS(app, supports_credentials=True)  # Allow cookies to be sent

# Initialize the database
init_db()

# Register blueprints for different modules
app.register_blueprint(book_routes_bp, url_prefix='/api/books')
app.register_blueprint(book_types_routes_bp, url_prefix='/api/book_types')
app.register_blueprint(user_routes_bp, url_prefix='/api/users')
app.register_blueprint(user_profiles_routes_bp, url_prefix='/api/user_profiles')
app.register_blueprint(loan_routes_bp, url_prefix='/api/loans')
app.register_blueprint(cities_routes_bp, url_prefix='/api/cities')
app.register_blueprint(categories_routes_bp, url_prefix='/api/categories')

@app.route('/')
def home():
    return "Welcome to the Library Management System API"

# Route to serve login.html from the frontend/static folder
@app.route('/login')
def login_page():
    return send_from_directory(os.path.join(app.static_folder), 'login.html')

if __name__ == '__main__':
    app.run(debug=True)
