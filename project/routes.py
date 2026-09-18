from flask import jsonify, request
from project.models import Amenity, User
from project import db
from flask import Blueprint

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route("/")
def home():
    message = {"message": "Hello, World!"}
    return jsonify(message)

@api_blueprint.route("/amenities", methods=["GET"])
def get_amenities():
    amenities = db.session.scalars(select(Amenity)).all()
    amenities_list = [{
        'id': amenity.id,
        'name': amenity.name,
        'type_id': amenity.type_id,
        'address': amenity.address,
    } for amenity in amenities]
    return jsonify(amenities_list)


@api_blueprint.route("/users", methods=["GET"])
def get_users():
    users = db.session.scalars(select(User)).all()
    user_list = [{
        'id': user.id,
        'username': user.username,
        'password': user.password,
    } for user in users]
    return jsonify(user_list), 200

@api_blueprint.route("/login", methods=["POST"])
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

@api_blueprint.route("/register", methods=["POST"])
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