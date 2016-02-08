from common import *

class DataService(object):
	def __init__(self):		
		self.dataCollection = mongoClient()[conf["mongo.dbName"]]["data"]

		# create the geo-index
		self.dataCollection.create_index([("loc" , pymongo.GEOSPHERE)])	

	def save(self, dataPoint):

		_filter = {
			"_id" : dataPoint.id
		}
		_update = dataPoint.dbObject()
		# perform an upsert
		self.dataCollection.replace_one(_filter, _update, upsert=True)

	def find(self, dataPoint, distance):
		"""
			Finds and computes scores of all datapoints within a certain distance of the given datapoint
		"""
		query = { 
          "loc" :{ 
			"$near" : { 
			  "$geometry" :{ 
			    "type" : "Point" ,
                  "coordinates" : [ dataPoint.latlong.longitude , dataPoint.latlong.latitude]
	            },
              "$maxDistance" : distance
	        }
		  }
		}		

		points = []
		for dbo in self.dataCollection.find(query):
			point = DataPoint(dbo["_id"])
			point.load(dbo)
			points.append({
				"point" : point.dict(),
				"distances" :  dataPoint.distance(point)
			})
		return points

	def clean(self):
		"""
			Removes all datapoints
		"""
		self.dataCollection.remove()

	def remove(self, Id):
		"""
			Removes one datapoint
		"""
		self.dataCollection.remove({"_id" : Id})
