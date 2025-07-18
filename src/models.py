from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(String(120), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password = db.Column(String(120), nullable=False)
    is_active = db.Column(Boolean(), nullable=False, default=True)

    favorites = relationship('Favorite', back_populates='user', cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

    def __str__(self):
        return self.username or f"User {self.id}"


class Character(db.Model):
    __tablename__ = 'character'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String(120), nullable=False)
    gender = db.Column(String(20))
    birth_year = db.Column(String(20))
    height = db.Column(String(10))

    favorites = relationship('Favorite', back_populates='character', cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "height": self.height
        }

    def __str__(self):
        return self.name or f"Character {self.id}"


class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String(120), nullable=False)
    climate = db.Column(String(120))
    terrain = db.Column(String(120))
    population = db.Column(String(120))

    favorites = relationship('Favorite', back_populates='planet', cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }

    def __str__(self):
        return self.name or f"Planet {self.id}"


class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    character_id = db.Column(db.Integer, ForeignKey('character.id'), nullable=True)
    planet_id = db.Column(db.Integer, ForeignKey('planet.id'), nullable=True)

    user = relationship('User', back_populates='favorites')
    character = relationship('Character', back_populates='favorites')
    planet = relationship('Planet', back_populates='favorites')

    def serialize(self):
        data = {
            "id": self.id,
            "user_id": self.user_id,
        }
        if self.character:
            data.update({"type": "character", "character": self.character.serialize()})
        if self.planet:
            data.update({"type": "planet", "planet": self.planet.serialize()})
        return data

    def __str__(self):
        if self.character:
            return f"Favorite Character: {self.character.name}"
        if self.planet:
            return f"Favorite Planet: {self.planet.name}"
        return f"Favorite #{self.id}"
