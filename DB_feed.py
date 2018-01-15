import requests
import time
from pymongo import MongoClient
import json
import numpy as np
from Model import FitModel

fm = FitModel()
# connect to the client
client = MongoClient()
#create the database
db = client.fraud_check
#create a new collection
fraud = db.fraud_check

while True:
    #capture the url event id
    response = requests.get("http://galvanize-case-study-on-fraud.herokuapp.com/data_point")
    event = response.json()
    url_eid = event['ticket_types'][0]['event_id']
    # check if the id is in the database
    if fraud.find().count() == 0:
        prob = fm.predict(event)
        prob = round(prob,2)
        if prob < 0.3:
            label = "low"
        elif 0.3 <= prob < 0.7:
            label = "medium"
        else:
            label = "high"
        fraud.insert_one({"event_id": url_eid, "prob_fraud": prob, "risk": label})
        print("insertion")
    db_check = fraud.find_one({"event_id": url_eid})
    if db_check != None:
        time.sleep(10)
    else:
        prob = fm.predict(event)
        prob = round(prob,2)
        if prob < 0.3:
            label = "low"
        elif 0.3 <= prob < 0.7:
            label = "medium"
        else:
            label = "high"
        fraud.insert_one({"event_id": url_eid, "prob_fraud": prob, "risk": label})
