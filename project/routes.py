from flask import jsonify, request, Blueprint
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required
)
from werkzeug.security import generate_password_hash, check_password_hash
from project.models import Amenity, User
from project import db
from sqlalchemy import select

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route("/")
def home():
    message = {"message": "Hello, World!"}
    return jsonify(message)

def pag_param_handler(data):
    # TODO what happens at upper limit
    page_default = 1
    per_page_default = 10
    offset_default = 0

    page_lower_lim = 1
    per_page_lower_lim = 10
    offset_lower_lim = 0

    def data_handler(d, default, lower_lim):
        if d is None:
            return default
        else:
            d = int(d)

        # under lower limit
        if d < lower_lim:
            return default
        else:
            return d

    return {
        'page': data_handler(data.args.get('page'), page_default, page_lower_lim),
        'per_page': data_handler(data.args.get('per_page'), per_page_default, per_page_lower_lim),
    }
        

@api_blueprint.route("/api/amenities", methods=["GET"])
@jwt_required()
def get_amenities():
    pag_params = pag_param_handler(request)
    page = db.paginate(
        select=select(Amenity), 
        page=pag_params['page'], 
        per_page=pag_params['per_page']
        )

    amenities_list = [{
        'id': amenity.id,
        'name': amenity.name,
        'type_id': amenity.type_id,
        'address': amenity.address,
    } for amenity in page]
    return jsonify(amenities_list)


@api_blueprint.route("/api/users", methods=["GET"])
@jwt_required()
def get_users():
    users = db.session.scalars(select(User)).all()
    user_list = [{
        'id': user.id,
        'username': user.username,
        'password': user.password,
    } for user in users]
    return jsonify(user_list), 200

# Create a route to authenticate your users and return JWTs.
@api_blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

    stmt = select(User).where(User.username == username)
    user = db.session.scalar(stmt)

    if user is None or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401
    else:
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": f"Welcome {user.username}", 
            "access_token":access_token})
        

@api_blueprint.route("/register", methods=["POST"])
def add_user():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # Missing credentials
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Check if user exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists. Please login.'}), 400

    hashed_password = generate_password_hash(password)
    
    new_user = User(
        username = username,
        password = hashed_password,
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'successfully added user'})