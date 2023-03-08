# Import dependencies
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify 


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.metadata.create_all(engine)

# Reflect the tables
Base.prepare(engine,reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    """List available api routes."""
    return (
        f"Available Hawaii Weather Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"The format for entering dates is year-month-date.<br/>"
        f"/api/v1.0/start<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    year_ago_date = dt.date(2017,8,23) - dt.timedelta(days = 365)
    
    # Perform a query to retrieve the data and precipitation scores
    Results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago_date).all()
    
    # Close Session                                                  
    session.close()

    # Return a dictionary with the date as key and prcp as value
    prcp_data = []
    for date, prcp in Results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)
        
    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

     # Perform a query to get data for stations
    total_number_of_stations = session.query(station.station).all()
    
    # Close Session                                                  
    session.close()

    # Convert list into normal list
    all_stations = list(np.ravel(total_number_of_stations))
    
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    most_active_stations = session.query(measurement.station,func.count(measurement.station)).order_by(func.count(measurement.station).desc()).group_by(measurement.station).all()

    
    # Close Session                                                  
    session.close()

    # Convert list into normal list
    tobs = list(np.ravel(most_active_stations))

    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    
    # Close Session                                                  
    session.close() 

    # Convert list into normal list
    start_date = list(np.ravel(results))
    
    return jsonify(start_date)


@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature between start and end dates entered
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Close Session                                                  
    session.close()

    # Convert list into normal list
    start_and_end_date = list(np.ravel(results))
    
    return jsonify(start_and_end_date)


if __name__ == '__main__':
    app.run(debug=True) 