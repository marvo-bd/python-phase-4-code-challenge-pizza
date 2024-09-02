from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationship
    pizzas = relationship(
        'Pizza',
        secondary='restaurant_pizzas',
        back_populates='restaurants'
    )

    # Serialization rules
    serialize_rules = ('-restaurant_pizzas.restaurant', '-restaurant_pizzas.pizza')

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationship
    restaurants = relationship(
        'Restaurant',
        secondary='restaurant_pizzas',
        back_populates='pizzas'
    )

    # Serialization rules
    serialize_rules = ('-restaurant_pizzas.restaurant', '-restaurant_pizzas.pizza')

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)

    # Relationships
    pizza = db.relationship('Pizza', backref='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', backref='restaurant_pizzas')

    def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id
        }

    @validates('price')
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30")
        return price

    # Serialization rules
    serialize_rules = (
        '-restaurant.restaurant_pizzas',
        '-pizza.restaurant_pizzas',
        ('pizza', {'only': ('id', 'name', 'ingredients')}),
        ('restaurant', {'only': ('id', 'name', 'address')})
    )

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
