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

class Validation(object):
	pointFormat = [
		("id", unicode),
		("latitude", float),
		("longitude", float)			
	]
	for tf in Properties.textFields:
		pointFormat.append((tf, unicode))


def cleanPointJSON(j):	
	for f in Properties.tokenizedTextFields:
		del j[f]
	return j	

class SaveDataResource(Resource):
	def post(self):
		try:			
			j = request.get_json(force=True)			
			validate(j, Validation.pointFormat)
			point = DataPoint(j["id"])
			point.latlong = LatLong(j["latitude"], j["longitude"])
			for tf in Properties.textFields:
				point.__setattr__(tf, j[tf])
			dataService.save(point)
			return {"message" : "ok"}, 200
		except AssertionError as e:
			return {"message" : e.message}, 400

class CleanDataResource(Resource):
	def delete(self):
		dataService.clean()
		return {"message" : "ok"}, 200

class RemoveDataResource(Resource):
	def delete(self, Id):
		dataService.remove(Id)
		return {"message" : "ok"}, 200

class FindNear(Resource):
	def post(self, distance=250):
		try:			
			j = request.get_json(force=True)			
			validate(j, Validation.pointFormat)
			point = DataPoint(j["id"])
			point.latlong = LatLong(j["latitude"], j["longitude"])
			for tf in Properties.textFields:
				point.__setattr__(tf, j[tf])
			points = dataService.find(point, distance)
			for p in points:
				p["point"] = cleanPointJSON(p["point"])
			result = {
				"point" : cleanPointJSON(point.dict()),
				"distance" : distance,
				"nearestPoints" : points
			}
			return result, 200			
		except AssertionError as e:
			return {"message" : e.message}, 400
		

api.add_resource(SaveDataResource, '/v1/point/')
api.add_resource(CleanDataResource, '/v1/points/clean')
api.add_resource(RemoveDataResource, '/v1/point/<string:Id>/')
api.add_resource(FindNear, '/v1/query/', '/v1/query/<float:distance>')

if __name__ == '__main__':
    app.run(debug=True)