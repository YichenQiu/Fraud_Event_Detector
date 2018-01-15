from __future__ import division
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)
#connect to the Mongo Client
client = MongoClient()
#create the database
db = client.fraud_check
#create a new collection
fraud = db.fraud_check

@app.route('/')
def index():
    docs = []
    for doc in fraud.find().sort('prob_fraud', -1):
        docs.append([doc['event_id'], doc['prob_fraud'], doc['risk']])
    return render_template('fraud.html', docs = docs)

if __name__ == "__main__":
    app.run()
