from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()

from flask_jwt_extended import JWTManager
from app.config import config_by_name
from flasgger import Swagger

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()
swagger = Swagger()


def create_app(config_name = "development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.config['SWAGGER'] = {
    'title': 'Beauty Shop API',
    'uiversion': 3,
    'securityDefinitions': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
        }
    }
}
    
    # initialize SQLAlchemy
    db.init_app(app)
    # initialize Flask-Migrate
    migrate.init_app(app, db)
    # initialize CORS
    cors.init_app(app, resources={r"/*": {"origins": [
    "http://127.0.0.1:5173", 
    "http://localhost:5173"
    ]}}, supports_credentials=True)

    jwt.init_app(app)
    swagger.init_app(app)

    from app import models
    from app.routes import (
        attendance_routes,
        auth_routes,
        contribution_routes,
        fine_routes,
        loan_routes,
        member_routes,
        payment_routes
    )
    return app
