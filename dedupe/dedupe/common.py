import pymongo
from pyhocon import ConfigFactory
from math import sin, cos, sqrt, atan2, radians
from text import TextUtils
from datetime import datetime

# load the configuration
conf = ConfigFactory.parse_file("conf/app.conf")

def mongoClient():
	# TODO make singleton / add other properties
	return  pymongo.MongoClient()	

class Properties(object):
	# fields used for computing distances
	textFields = set(conf["data.textFields"])
	# fields derived from textFields
	tokenizedTextFields = set(map(lambda _ : "tokenized_" + _, conf["data.textFields"]))

class LatLong(object):
	"""
	Represents a (latitude, longitude) tuple.
	"""
	@staticmethod
	def distance(l1, l2):
		# Source: http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
		# Radius of earth in kilometers
		R = 6373.0		 
		# convert to radians
		lat1 = radians(l1.latitude)
		lon1 = radians(l1.longitude)
		lat2 = radians(l2.latitude)
		lon2 = radians(l2.longitude)

		# haversine formular
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		# covert to meters
		return R * c * 1000

	def __init__(self, latitude, longitude):
		"""
			Init a LatLong object
		"""
		self.latitude = latitude
		self.longitude = longitude

class TextDistance(object):
	"""
	Contains various distances for text vectors
	"""
	@staticmethod
	def jaccard(v1, v2):
		"""
		Compute the Jaccard Distance / Dissimilarity. Read More: https://en.wikipedia.org/wiki/Jaccard_index

		"""


		v1 = set(v1)
		v2 = set(v2)		
		u = len(v1.union(v2))
		# to prevent divide by 0. 
		if u == 0:
			# Since no information is present, assume dissimilar vectors
			return 1
		# 1 - jaccard_index(u, v)
		return 1 - float(len(v1.intersection(v2))) / len(v1.union(v2))

class ScoreCombiner(object):
	"""
	Interface for combining multiple distances {distance_name -> distance}
	"""	
	def combine(self, scoreDict):
		"""
		Combines multiple distances into a single 'score'
		"""
		raise NotImplementedError()

class WeightedScoreCombiner(ScoreCombiner):
	def __init__(self, fields, weights = None):
		"""
			Combine multiple distances using a weighted average 
		"""
		n = len(fields)		
		if not weights:
			# if weights is not defined, use a simple average i.e uniform weights
			_n = float(n)
			weights = {}
			for field in fields:
				weights[field] = 1 / _n

		assert len(weights) == n
		self.weights = weights
		self.sum = sum(weights.values())

	def combine(self, scoreDict):
		score = 0.0
		for f, v in scoreDict.iteritems():
			score += v * self.weights[f]
		return score / self.sum

# TODO MAKE THIS CONFIGURABLE
ScoreCombiner._combiner = WeightedScoreCombiner(Properties.tokenizedTextFields)

class DataPoint(object):
	# the set of 'allowed' fields in a datapoint
	fields = (set(Properties.textFields)
				.union(Properties.tokenizedTextFields)
				.union(["id", "latlong"]))

	def __init__(self, Id):
		"""
			Init a DataPoint
		"""
		self.id = Id
		self.latlong = None

	def __setattr__(self, name, value):
		# only allow setting of allowed fields
		if name in DataPoint.fields:
			self.__dict__[name] = value
			# if the field is a text field, add an additional field	which holds the tokenized text
			if name in Properties.textFields:
				self.__dict__["tokenized_" + name] = TextUtils.tokenizeText(value)
		else:
			# TODO convert this to log
			print "WARN: The field '{}' is not being set".format(name)

	def dbObject(self):		
		"""
			Convert the datapoint into a Mongo-serializable format
		"""
		p = self.dict()
		# this is the format used for Mongo's geo-index
		p["loc"] = {
	        "type" : "Point",
	        "coordinates" : [self.latlong.longitude, self.latlong.latitude]
		}
		# the document id
		p["_id"] = self.id
		del p["id"]		
		# store the last modified time
		p["modified"] = datetime.now()		
		return p

	def dict(self):
		"""
			Conver the datapoint into a dictionary
		"""
		p = {}
		p["loc"] = {
	        "latitude" : self.latlong.latitude,
	        "longitude" : self.latlong.longitude	        
		}
		p["id"] = self.id

		for tf in Properties.textFields:
			if tf not in self.__dict__:
				continue			
			p[tf] = self.__dict__[tf]

		for tf in Properties.tokenizedTextFields:
			if tf not in self.__dict__:
				continue			
			p[tf] = self.__dict__[tf]		
		return p

	def load(self, dbo):		
		"""
			Loads the fields of the datapoint from the mongo / dict-like object
		"""
		lon, lat = dbo["loc"]["coordinates"]
		self.latlong = LatLong(lat, lon)
		for tf in Properties.textFields:
			# set only the text fields, since the tokenized text fields are automatically generated
			self.__setattr__(tf, dbo[tf])

	def distance(self, other):
		"""
			Return a dictionary of different distances from another data point
		"""
		dist = {}		
		tokDistances  = {}
		# compute text i.e jaccard distance from the other datapoint
		for tf in Properties.tokenizedTextFields:
			dist[tf] = TextDistance.jaccard(self.__dict__[tf], other.__dict__[tf])		
		# combine the text distances into one 'score'
		dist["overallDistance"] = ScoreCombiner._combiner.combine(dist)
		# compute the geo-distance 
		dist["geo-distance"] = LatLong.distance(self.latlong, other.latlong)
		return dist