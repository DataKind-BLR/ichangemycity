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

	def find(self, dataPoint, distance):
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

if __name__ == '__main__':
	dp = DataPoint("")
	dp.title = "This is ome danmed title with some other sutff going on near govindnagar."
	dp.description = "This is ome other damned text"
	dp.latlong = LatLong(1.3, 3.42)
	print DataService().find(dp)