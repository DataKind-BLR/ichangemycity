from flask import Flask, request
from flask_restful import Resource, Api
from services import *
from common import *

dataService = DataService()

app = Flask(__name__)
api = Api(app)


def validate(j, format):
	for field, t in format:
		assert field in j, "Field {} is absent".format(field)
		assert isinstance(j[field], t), "Expected type {}, but got type {} for field {}".format(t, type(j[field]), field)

class SaveDataResource(Resource):
	format = [
		("id", unicode),
		("latitude", float),
		("longitude", float)			
	]
	for tf in Properties.textFields:
		format.append((tf, unicode))

	def post(self):
		try:			
			j = request.get_json(force=True)			
			validate(j, SaveDataResource.format)
			point = DataPoint(j["id"])
			point.latlong = LatLong(j["latitude"], j["longitude"])
			for tf in Properties.textFields:
				point.tf = j[tf]
			dataService.save(point)
			return {"message" : "ok"}, 200
		except AssertionError as e:
			return {"message" : e.message}, 400


api.add_resource(SaveDataResource, '/v1/save/')

if __name__ == '__main__':
    app.run(debug=True)