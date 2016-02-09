import json
import math
import codecs
import pandas as pd
import requests
import argparse
import sys
import time

ID_FIELD = "complaint_complaint_iid"
TEXT_FIELDS = {
	"" : "title",
	"complaint_description" : "description",
}
LATITUDE = "complaint_latitude"
LONGITUDE = "complaint_longitude"

HOST = "http://localhost:5000"

def load(path):	
	print "Loading Data into the API"
	df = pd.read_csv(path)
	# CLEAR UP OLD DATA
	requests.delete(HOST + "/v1/points/clean")
	total = len(df)
	startTime = time.time()
	for i, (index, row) in enumerate(df.iterrows()):		
		if math.isnan(row[LATITUDE]) or math.isnan(row[LONGITUDE]):
			continue

		data = {
			"id" : str(row[ID_FIELD]),
			"title" : row["complaint_title"],
			"description" : str(row["complaint_description"]),
			"latitude" : row[LATITUDE],
			"longitude" : row[LONGITUDE],
		}		
		#print data
		
		response = requests.post(HOST + "/v1/point/", json=data)
		
		if response.status_code != 200:
			print response.text, data

		if i % 1000 == 0:
			print "{} of {} done. Elapsed Seconds: {}".format(i, total, time.time() - startTime)

	print "{} done. Elapsed Seconds: {}".format(total, time.time() - startTime)
		
def query(path, outPath):
	print "Querying the API"
	df = pd.read_csv(path)
	total = len(df)
	startTime = time.time()
	with codecs.open(outPath, "w", "utf-8") as writer:
		for i, (index, row) in enumerate(df.iterrows()):		
			if math.isnan(row[LATITUDE]) or math.isnan(row[LONGITUDE]):
				continue

			data = {
				"id" : str(row[ID_FIELD]),
				"title" : row["complaint_title"],
				"description" : str(row["complaint_description"]),
				"latitude" : row[LATITUDE],
				"longitude" : row[LONGITUDE],
			}		
			
			url = "{}/v1/query/".format(HOST)		
			response = requests.post(url, json=data)

			if response.status_code != 200:
				print "ERR:", response.status_code, data["id"]


			writer.write(json.dumps(response.json()))
			writer.write("\n")

			if i % 1000 == 0:
				print "{} of {} done. Elapsed Seconds: {}".format(i, total, time.time() - startTime)

		print "{} done. Elapsed Seconds: {}".format(total, time.time() - startTime)

if __name__ == '__main__':	
	parser = argparse.ArgumentParser()
	parser.add_argument("path", help="path of the complaints csv file")
	parser.add_argument("-o", "--out", help="output path of the results")
	parser.add_argument("-l", "--load", help="loads the data",
                    action="store_true")
	parser.add_argument("-q", "--query", help="queries the api to fetch JSON results, stores output in OUT",
                    action="store_true")

	
	args = parser.parse_args()
	
	if	args.load:
		load(args.path)
	
	if args.query:
		if args.out is None:
			print "OUT required if querying"
			sys.exit(-1)
		query(args.path, args.out)
	
	if not args.load and not args.query:
		print "No action specified"