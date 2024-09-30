from flask import Flask
from .routes import book_routes_bp, book_types_routes_bp, user_routes_bp, loan_routes_bp, user_profiles_routes_bp, cities_routes_bp
from ..database import init_db 

app = Flask(__name__)

# Initialize the database
init_db()

# Register blueprints for different modules
app.register_blueprint(book_routes_bp, url_prefix='/api/books')
app.register_blueprint(book_types_routes_bp, url_prefix='/api/book_types')
app.register_blueprint(user_routes_bp, url_prefix='/api/users')
app.register_blueprint(user_profiles_routes_bp, url_prefix='/api/user_profiles')
app.register_blueprint(loan_routes_bp, url_prefix='/api/loans')
app.register_blueprint(cities_routes_bp, url_prefix='/api/cities')



@app.route('/')
def home():
    return "Welcome to the Library Management System API"

if __name__ == '__main__':
    app.run(debug=True)
