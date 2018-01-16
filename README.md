# Case Study: Fraud Event Detector
* Trained model using real-world data to detect fraud events in real-time
* Created web app to inform company of high risk fraud events in real-time
* To run the app using localhost, type `python DB_feed` in terminal to populate the database, then type `python app.py` in terminal and view the app in localhost:5000

## Pipeline

(1) Model Building ----->   (2) Fit Model

(2) Fit Model     <----->   (3) DB feed    <------>   (4) Web

(3) DB Feed ------>  (5) Database  ------->  (6) Dashboard App


## Model Prediction
files for model predictions

`Model.py`
  * unpack pickle model
  * parse dictionary object
  * returns predicted probability of fraud from a Pandas df of features

`DB_feed.py`
  * makes a web request
  * sends dict file to model
  * calls Model.py to calculate the probability
  * sends {event_id, probability of fraud, risk label} to Database

## Database

MongoDB
  * stores data sent by `DB_feed.py`


## Dash App
files for pulling data from database

`app.py`
  * pulls data from Database
  * sorts data
  * starts web app

`fraud.html`
  * calls function in app.py to obtain data for html presentation
  * creates front-end webpage
