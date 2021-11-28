
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

## Display Keys


#Reflect the Database

# Base.classes.keys()
##['measurement', 'station']

session=Session(engine)

#### Create Classes
measurement = Base.classes.measurement
station = Base.classes.station

### Flask Set Up
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date(yyyy-mm-dd)<br/>"
        f"/api/v1.0/start_date(yyyy-mm-dd)/end_date(yyyy-mm-dd)<br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
   ##Return the precipitation data for the last year"""
   # Calculate the date 1 year ago from last date in database
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   # Query for the date and precipitation for the last year

   precipitation = session.query(measurement.date, measurement.prcp).\
       filter(measurement.date >= prev_year).all()
   session.close()
   # Dict with date as the key and prcp as the value
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)
   

@app.route("/api/v1.0/stations")
def stations():
   ####Return a list of stations.
   results = session.query(station.station).all()
   # Unravel results into a 1D array and convert to a list
   stations = list(np.ravel(results))
   return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    
    ##return list of all TOBS
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results=session.query(measurement.date,measurement.tobs).filter\
        (measurement.date>= prev_year).filter(measurement.station=='USC00519281')\
        .order_by(measurement.date).all()
    
    tobs1617=[]
    for date, tobs in results:
        tobs_dict={}
        tobs_dict["date"]= date
        tobs_dict["tobs"]=tobs
        
        tobs1617.append(tobs_dict)
    return jsonify(tobs1617)

@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    
    #Get min, avg and max for start date that user states
    results=session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
        .filter(measurement.date>= start_date).all()
    #Create dictionary for start date
    tobs_start=[]
    for min, max, avg in results:
        tobs_start_dict={}
        tobs_start_dict["min_temp"]=min
        tobs_start_dict["max_temp"]=max
        tobs_start_dict["avg_temp"]=avg
        tobs_start.append(tobs_start_dict)
    return jsonify(tobs_start)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_dates(start_date, end_date):

    #get the querries for the time frame between start/end dates user deems
    results= session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
        .filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    #create dictionary to get the data for max, min, avg in timeframe
    start_end_tobs=[]
    for min, avg, max in results:
        st_en_tobs={}
        st_en_tobs["min_temp"]= min
        st_en_tobs["max_temp"]=max
        st_en_tobs["avg_temp"]=avg
        start_end_tobs.append(st_en_tobs)
    return jsonify(start_end_tobs)

if __name__ == '__main__':
    app.debug = True
    app.run()


    
