"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorites

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200

# ___________________________________________________

@app.route('/users', methods=['GET'])
def get_all_user():
    user = User.query.all()
    user_serialized = [data.serialize() for data in user]
    return jsonify(user_serialized), 200

# ___________________________________________________

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(user.serialize()), 200

# ___________________________________________________

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()


    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Faltan campos obligatorios: username, email, password"}), 400

  
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "El nombre de usuario ya existe"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "El email ya está registrado"}), 400


    new_user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"], 
        is_active=True
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": "Usuario creado", "user": new_user.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ____________________________________________________

@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    people_serialized = [data.serialize() for data in people]
    return jsonify(people_serialized), 200

# ___________________________________________________

@app.route('/people/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = People.query.get(character_id)
    if not character:
        return jsonify({"error": "Character no encontrado"}), 404
    return jsonify(character.serialize()), 200

# ___________________________________________________

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    planets_serialized = [data.serialize() for data in planets]
    return jsonify(planets_serialized), 200

# ___________________________________________________

@app.route('/planets/<int:planet_id>', methods=["GET"])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200

# ___________________________________________________

@app.route('/favorites/<int:user_id>', methods=['GET'])
def get_favorites(user_id):
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    if not favorites:
        return jsonify({"error": "Favoritos no localizados"}), 404
    return jsonify([favorite.serialize() for favorite in favorites]), 200

# ___________________________________________________

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_fav_character(people_id):
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "El id del usuario es obligatorio"}), 400


    user = User.query.get(user_id)
    character = People.query.get(people_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if not character:
        return jsonify({"error": "Personaje no encontrado"}), 404

    # Crear el nuevo favorito
    new_favorite = Favorites(
        user_id=user_id,
        planet_id=None,
        people_id=people_id
    )

    try:
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"success": "Personaje agregado a favoritos", "favorite": new_favorite.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ___________________________________________________

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_fav_character(people_id):
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "El id del usuario es obligatorio"}), 400


    favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404

    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"success": f"Favorito con ID {people_id} ha sido eliminado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ___________________________________________________

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet(planet_id):
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "El id del usuario es obligatorio"}), 400

    # Verificar si el usuario y el planeta existen
    user = User.query.get(user_id)
    planet = Planets.query.get(planet_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if not planet:
        return jsonify({"error": "Planeta no encontrado"}), 404

    # Crear el nuevo favorito
    new_favorite = Favorites(
        user_id=user_id,
        planet_id=planet_id,
        people_id=None
    )

    try:
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"success": "Planeta agregado a favoritos", "favorite": new_favorite.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ___________________________________________________

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_fav_planet(planet_id):
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "El id del usuario es obligatorio"}), 400

  
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404

    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"success": f"Favorito con ID {planet_id} ha sido eliminado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ___________________________________________________

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
