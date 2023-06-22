#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in Scientist.query.all()]
        return make_response(jsonify(scientists), 200)
    
    def post(self):
        try:
            data = request.get_json()
            scientist = Scientist(**data)
            db.session.add(scientist)
            db.session.commit()
            return make_response(jsonify(scientist.to_dict(only=('id','name', 'field_of_study'))), 201)
        except Exception as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
        
    
api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        try:
            scientist = Scientist.query.get(id)
            return make_response(jsonify(scientist.to_dict(only=('name', 'field_of_study', 'id', 'missions', '-missions.scientist'))), 200)
        except Exception as e:
            return make_response(jsonify({"error": "Scientist not found"}), 404)
        
    def delete(self, id):
        try:
            scientist = db.session.get(Scientist, id)
            db.session.delete(scientist)
            db.session.commit()
            return make_response(jsonify({}), 204)
        except Exception as e:
            return make_response(jsonify({"error": "Scientist not found"}), 404)
        
    def patch(self, id):
        try:
            scientist = Scientist.query.filter(Scientist.id == id).first()
            if not scientist:
                return make_response(jsonify({"error": "Scientist not found"}), 404)
            # import ipdb; ipdb.set_trace()
            for attr in request.get_json():
                setattr(scientist, attr, request.get_json()[attr])
            db.session.add(scientist)
            db.session.commit()
            return make_response(jsonify(scientist.to_dict()), 202)
        except Exception as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
        
api.add_resource(ScientistById, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planets = [planets.to_dict() for planets in Planet.query.all()]
        return make_response(jsonify(planets), 200)
    
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        try:
            data = request.get_json()
            mission = Mission(**data)
            db.session.add(mission)
            db.session.commit()
            return make_response(jsonify(mission.to_dict()), 201)
        except Exception as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
        
api.add_resource(Missions, '/missions')
if __name__ == '__main__':
    app.run(port=5555, debug=True)
