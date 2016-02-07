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
