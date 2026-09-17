from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, select
from typing import List
import data_import
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
if os.getenv('DATABASE_TYPE') == 'sqlite':
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/{os.getenv('DATABASE_NAME')}"
elif os.getenv('DATABASE_TYPE') == 'postgres':
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

class Amenity(db.Model):
    __tablename__ = 'amenity'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("amenity_type.id"))
    address: Mapped[str] = mapped_column(String())

    amenity_type: Mapped["AmenityType"] = relationship(back_populates="amenities")

class AmenityType(db.Model):
    __tablename__ = 'amenity_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] =  mapped_column(String(), nullable=False)

    amenities: Mapped[List["Amenity"]] = relationship(back_populates="amenity_type")

db.init_app(app)

@app.route("/")
def home():
    message = {"message": "Hello, World!"}
    return jsonify(message)

@app.route("/amenities", methods=["GET"])
def get_amenities():
    amenities = db.session.scalars(select(Amenity)).all()
    amenities_list = [{
        'id': amenity.id,
        'name': amenity.name,
        'type_id': amenity.type_id,
        'address': amenity.address,
    } for amenity in amenities]
    return jsonify(amenities_list)


@app.route("/users", methods=["GET"])
def get_users():
    users = db.session.scalars(select(User)).all()
    user_list = [{
        'id': user.id,
        'username': user.username,
        'password': user.password,
    } for user in users]
    return jsonify(user_list), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    stmt = select(User).where(User.username ==  username and User.password == hashed_password)
    user = db.session.scalar(stmt)
    if user:
        return jsonify({"message": f"Welcome {user.username}"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/register", methods=["POST"])
def add_user():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    new_user = User(
        username = username,
        password = hashed_password,
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'successfully added user'})

def refresh_db():
    params = data_import.params
    for param in params:
        df = data_import.pull_data(param=param)
        formatted_df = data_import.format_data_for_db(param=param, df=df)
        formatted_df.to_sql(name='amenity', con=db.engine, if_exists='append', index=False)
        print(f"Update amenity with {param['id']}")
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        refresh_db()
    app.run(debug=True)