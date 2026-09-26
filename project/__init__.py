from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, inspect

import os
from click import echo

import project.data_import as data_import

# initialize database engine
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def load_amenity_type_data():
    from project.models import AmenityType
    amenity_types = ['Library', 'Park', 'Community Centre', 'Civic Centre']
    for amenity_type in amenity_types:
         db.session.add(AmenityType(name=amenity_type))
    db.session.commit()

def load_amenity_data():
    # get each params for each dataset
    dataset_params = data_import.params

    for param in dataset_params:
        # pull and prepare data from toronto open
        df = data_import.pull_data(param=param)
        formatted_df = data_import.format_data_for_sql(param=param, df=df)

        # No need to commit, pandas handles that automatically
        formatted_df.to_sql(name='amenity', con=db.engine, if_exists='append', index=False)
        echo(f"Update amenity with {param['id']}")

def db_init(app):
    db.init_app(app)

    # Check if the database needs to be initialized
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    inspector = inspect(engine)
    if not inspector.has_table("amenity") or not inspector.has_table("user"):
        with app.app_context():
            db.drop_all()
            db.create_all()
            app.logger.info('Initialized the database!')
    else:
        app.logger.info('Database already initialized.')

    from project.models import AmenityType, Amenity

    # load data if tables are empty
    with app.app_context():
        if not db.session.query(AmenityType).first():
            load_amenity_type_data()
        if not db.session.query(Amenity).first():
            load_amenity_data()

def register_blueprints(app):
    from project.routes import api_blueprint
    app.register_blueprint(api_blueprint)

def create_app():
    # Create the Flask application
    app = Flask(__name__)
    jwt = JWTManager(app)

    # Allows for requests from different domains
    CORS(app)

    # Configure the Flask application
    config_type = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object(config_type)

    # register routes
    register_blueprints(app)

    # Initialize database
    db_init(app=app)

    return app