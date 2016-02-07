import pymongo
from pyhocon import ConfigFactory
from math import sin, cos, sqrt, atan2, radians
from text import TextUtils
from datetime import datetime

conf = ConfigFactory.parse_file("conf/app.conf")

def mongoClient():
	# TODO make single ton / add other properties
	return  pymongo.MongoClient()	

class Properties(object):
	textFields = conf["data.textFields"]

class LatLong(object):

	@staticmethod
	def distance(l1, l2):
		R = 6373.0		 
		lat1 = radians(l1.latitude)
		lon1 = radians(l1.longitude)
		lat2 = radians(l2.latitude)
		lon2 = radians(l2.longitude)
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		# in meters
		return R * c * 1000

	def __init__(self, latitude, longitude):
		self.latitude = latitude
		self.longitude = longitude


class DataPoint(object):
	fields = set(Properties.textFields).union(["id", "latlong"])
	def __init__(self, Id):
		self.id = Id
		self.latlong = None

	def __setattr__(self, name, value):		
		if name in DataPoint.fields:
			self.__dict__[name] = value		
		else:
			# TODO convert this to log
			print "WARN: The field '{}' is not being set".format(name)

	def dbObject(self):		
		p = {}
		p["loc"] = {
	        "type" : "Point",
	        "coordinates" : [self.latlong.longitude, self.latlong.latitude]
		}
		p["_id"] = self.id

		for tf in Properties.textFields:
			if tf not in self.__dict__:
				continue
			text = self.__dict__[tf]			
			p[tf] = text
			p["tokenized_" + tf] = TextUtils.tokenizeText(text)

		p["modified"] = datetime.now()

		return p
		
