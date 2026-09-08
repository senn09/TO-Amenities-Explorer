from flask import Flask, jsonify, request
import sqlite3
import os
import hashlib
import dotenv
import wraps

API_TOKEN = os.getenv("API_TOKEN")

app = Flask(__name__)

def require_token(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        token = request.headers.get("Authorization")
        if token != f"Bearer {API_TOKEN}":
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args,**kwargs)
    return decorated_function()


def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/init", methods=["GET"])
def init_db():
    conn = get_db_connection()
    conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL, 
            price REAL NOT NULL
            )        
            """)

    conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            email TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL
            )        
            """)
    conn.commit()
    conn.close()
    return jsonify({"message": "Database initialized successfully"}), 201

@app.route("/")
def home():
    message = {"message": "Hello, World!"}
    return jsonify(message)

@app.route("/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return jsonify([dict(product) for product in products])

@app.route("/products", methods=["POST"])
@require_token
def create_product():
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    new_product_id = cursor.lastrowid
    conn.close()

    new_product = {
        "id": new_product_id, 
        "name": name,
        "price": price
    }

    message = {
        "message": "Product created successfully",
        "product": new_product
    }

    return jsonify(message), 201

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO users (email, password) VAlUES (?, ?)", (email, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError: # email already exists
        return jsonify({"error": "Email already exists"}), 409

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password)).fetchone()
    conn.close()

    if user:
        return jsonify({"message": f"Welcome {email}"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)