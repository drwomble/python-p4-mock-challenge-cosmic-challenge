from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    # Add relationship
    missions = db.relationship('Mission', back_populates='planet', cascade='all')
    scientists = association_proxy('missions', 'scientist')
    # Add serialization rules
    serialize_only = ('id', 'name', 'distance_from_earth', 'nearest_star')
    
    def __repr__(self):
        return f'<Planet {self.id}: {self.name}>'


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add relationship
    missions = db.relationship('Mission', back_populates='scientist', cascade='all')
    planets = association_proxy('missions', 'planet')
    # Add serialization rules
    serialize_only = ('id', 'name', 'field_of_study')
    serialize_rules = ('-created_at', '-updated_at')
    # Add validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError('scientist must have a name')
        return name
    
    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        if not field_of_study:
            raise ValueError('Scientist must have a field of study')
        return field_of_study
    
    def __repr__(self):
        return f'<Scientist {self.id}: {self.name}>'


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)

    # Add relationships
    planet = db.relationship('Planet', back_populates='missions')
    scientist = db.relationship('Scientist', back_populates='missions')
    # Add serialization rules
    serialize_only = ('id', 'name', 'planet_id', 'scientist_id', 'planet', 'scientist')
    # Add validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError('Mission must have a name, try and think of something cool')
        return name
    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        if not scientist_id:
            raise ValueError('Mission must have a scientist_id')
        return scientist_id
    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        if not planet_id:
            raise ValueError('Mission must have a planet_id')
        return planet_id
    
    def __repr__(self):
        return f'<Mission {self.id}>'
# add any models you may need.
