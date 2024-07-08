from flask import Flask
from flask_cors import CORS
from config import Config
from app.database import db, migrate  # Ensure db is imported from app/database.py
from app.utils.database import init_db
import logging
from logging.handlers import RotatingFileHandler
import os 

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)  # Enable CORS for the Flask app
    app.config.from_object(config_class)
    app.debug = True

    db.init_app(app)  # Initialize SQLAlchemy with the Flask app
    migrate.init_app(app, db)

    from app.routes import api
    app.register_blueprint(api.bp, url_prefix='/api')

    with app.app_context():
        init_db()  # Optionally, initialize the database

       # Configure logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/your_app.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('YourApp startup')

    return app