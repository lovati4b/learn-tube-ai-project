from flask import Flask
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS # <--- IMPORT IT HERE

# Initialize extensions (outside the factory function so they are globally accessible)
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()

    app = Flask(__name__)

    # --- Initialize CORS ---
    # This should be done early, after app is created.
    # CORS(app) will allow all origins, which is fine for development.
    # For production, you would restrict it, e.g.:
    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}) 
    # (Adjust port if your Vue dev server uses a different one)
    CORS(app) # <--- INITIALIZE IT HERE
    # -----------------------

    # --- Database Configuration ---
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(app.instance_path, 'learn_tube_ai.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # -----------------------------

    # Initialize other extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # --- Ensure instance folder exists ---
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass 
    # ------------------------------------

    # Import and register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Import models here so Flask-Migrate can find them
    from . import models 

    print("Flask app created, extensions initialized (including CORS), and blueprint registered.") # Updated print
    if os.environ.get('ANTHROPIC_API_KEY'):
        print("ANTHROPIC_API_KEY is SET.")
    else:
        print("ANTHROPIC_API_KEY not found. Using MOCK LLM client (implicitly).")
    
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    return app