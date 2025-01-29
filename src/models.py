from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    
class Favorites(db.Model):
    __tablename__ = "favorites"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("user.id"), nullable=False)
    people_id = db.Column(db.Integer, ForeignKey("people.id"), nullable=True)
    planet_id = db.Column(db.Integer, ForeignKey("planets.id"), nullable=True)

    user = relationship("User", backref="favorites")
    people = relationship("People", backref="favorites")
    planet = relationship("Planets", backref="favorites")

    def __repr__(self):
        return f'Favorites User {self.user_id}'    
    
    def serialize(self):
        return {
            "user_id": self.user.serialize() if self.user else None,
            "character": self.people.serialize() if self.people else None,
            "planet": self.planet.serialize() if self.planet else None
        }

class People(db.Model):
    __tablename__ = "people"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    homeworld = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return f'<People {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "homeworld": self.homeworld
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    __tablename__ = "planets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    climate = db.Column(db.String(80), unique=False, nullable=False)
    terrain = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return f'<Planets {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain
            # do not serialize the password, its a security breach
        }