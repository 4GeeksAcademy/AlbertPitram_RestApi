import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False


db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
MIGRATE = Migrate(app, db)
CORS(app)
setup_admin(app)

with app.app_context():
    db.create_all()

CURRENT_USER_ID = 1

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    return jsonify([p.serialize() for p in people])

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Character.query.get_or_404(people_id)
    return jsonify(person.serialize())

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets])

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify(planet.serialize())

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users])

@app.route('/users/favorites', methods=['GET'])
def get_favorites():
    user = User.query.get_or_404(CURRENT_USER_ID)
    favs = []
    for f in user.favorites:
        if f.planet:
            favs.append({"type": "planet", "id": f.planet.id, "name": f.planet.name})
        elif f.character:
            favs.append({"type": "character", "id": f.character.id, "name": f.character.name})
    return jsonify(favs)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user = User.query.get_or_404(CURRENT_USER_ID)
    planet = Planet.query.get_or_404(planet_id)
    existing = Favorite.query.filter_by(user_id=user.id, planet_id=planet.id).first()
    if existing:
        return jsonify({"message": "Already favorited"}), 400
    fav = Favorite(user_id=user.id, planet_id=planet.id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": "Favorite added"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):
    user = User.query.get_or_404(CURRENT_USER_ID)
    character = Character.query.get_or_404(people_id)
    existing = Favorite.query.filter_by(user_id=user.id, character_id=character.id).first()
    if existing:
        return jsonify({"message": "Already favorited"}), 400
    fav = Favorite(user_id=user.id, character_id=character.id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": "Favorite added"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user = User.query.get_or_404(CURRENT_USER_ID)
    fav = Favorite.query.filter_by(user_id=user.id, planet_id=planet_id).first()
    if not fav:
        return jsonify({"message": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(people_id):
    user = User.query.get_or_404(CURRENT_USER_ID)
    fav = Favorite.query.filter_by(user_id=user.id, character_id=people_id).first()
    if not fav:
        return jsonify({"message": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
