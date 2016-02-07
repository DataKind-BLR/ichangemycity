from common import *

class DataService(object):
	def __init__(self):
		self.dataCollection = mongoClient()[conf["mongo.dbName"]]["data"]
		self.dataCollection.create_index([("loc" , pymongo.GEOSPHERE)])	

	def save(self, dataPoint):
		_filter = {
			"_id" : dataPoint.id
		}
		_update = dataPoint.dbObject()
		self.dataCollection.replace_one(_filter, _update, upsert=True)

	def find(self, dataPoint, distance, combiner=None):
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
		self.dataCollection.remove()

	def remove(self, Id):
		self.dataCollection.remove({"_id" : Id})
