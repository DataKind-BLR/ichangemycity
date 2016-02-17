# ichangemycity

## About the organization:

Janaagraha was established in 2001 as a non-profit organisation that works on combining the efforts of both the government and the citizens to transform our cities and ensure better quality of life by improving quality of urban infrastructure and services and quality of citizenship. Their civic portal IChangeMyCity promotes civic action at a local neighborhood level.

Mission:

To cultivate and nurture the spirit of active citizenship..

## About this repository
This repo holds code and documentation for DataKind Bangalore's Data Corps with IChangeMyCity.

Currently, this holds code for a real-time deduplication engine, built using python. (read the hackpad for more details)

## Getting Started
### Setup
To run the API, you need `python 2.7`, `mongodb 3.x` and `pip` installed.
- Install requirements with `pip install -r requirements.txt`
- Run `python -m nltk.downloader all` to install NLTK resources
- Configure the API after editing `app.conf`
- Startup the API with `python api.py`

To load the ICMC data into the API and make it available on the API, run `scripts/icmc.py`


### Documentation
- The API docs are built using [Swagger][1].
- To view the latest documentation and play around with the API, use this [link][2]


## Links
- Hackpad: https://dkblr.hackpad.com/Janaagraha-j3k5iq6Ywal
- IChangeMyCity: http://www.ichangemycity.com/
- DataKind: http://www.datakind.org




  [1]: http://swagger.io/ "Swagger"
  [2]: http://editor.swagger.io/#/?import=https://raw.githubusercontent.com/DataKind-BLR/ichangemycity/master/dedupe/docs/swagger.yaml
