import json
import math
import codecs
import pandas as pd
import requests

PATH = "/home/samarth/workspaces/datakind-workspace/ichangemycity/Sprint-ComplaintsDeduplication/icmyc_complaints.csv"

ID_FIELD = "complaint_complaint_iid"
TEXT_FIELDS = {
	"" : "title",
	"complaint_description" : "description",
}
LATITUDE = "complaint_latitude"
LONGITUDE = "complaint_longitude"

HOST = "http://localhost:5000"

def load():
	df = pd.read_csv(PATH)
	# CLEAR UP OLD DATA
	requests.delete(HOST + "/v1/points/clean")
	total = len(df)
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
			print "{} of {} done".format(i, total)
		
def query():
	df = pd.read_csv(PATH)
	total = len(df)
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
			print response.text, data["id"]

		print response.json()
		if i % 1000 == 0:
			print "{} of {} done".format(i, total)

if __name__ == '__main__':	
	query()