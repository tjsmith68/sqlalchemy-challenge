import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start date)<br/>"
        f"/api/v1.0/(start date)/(end date)<br/>"
        f"*** Note: (start date) and (end date) should contain date values as YYYY-MM-DD ***"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a json of all precipitation data"""
    # Query measurements for precip data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert precip data into a dictionary

    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all Stations"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)
 

@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations"""

    # Get station with most measurements
    most_active = session.query(Measurement.station, func.count(Measurement.date).\
              label('meas_count')).group_by(Measurement.station).order_by(desc('meas_count')).first()

    (active_station, active_count) = most_active
    # Get last date in measurements

    first_row = session.query(Measurement).order_by(Measurement.date.desc()).first()
    final_date = first_row.date

    # Calculate the date one year from the last date in data set.
    
    end_date = dt.datetime.strptime(final_date, '%Y-%m-%d')
    start_date = end_date - dt.timedelta(days=365)
    start_date_short = start_date.date()
    end_date_short = end_date.date()

    # Perform a query to retrieve the date and tobs data

    results = session.query(Measurement.date, Measurement.tobs).\
                     filter((Measurement.date >= start_date_short) &
                            (Measurement.date <= end_date_short) &
                            (Measurement.station == active_station)) 

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def date_range_temps(start_date, end_date):

    """Return Temperature stats for date range"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query Temp stats
    results = session.query(Measurement,
                            func.min(Measurement.tobs).label('min_temp'), 
                            func.max(Measurement.tobs).label('max_temp'),
                            func.avg(Measurement.tobs).label('avg_temp')).\
                            filter((Measurement.date >= start_date) &
                                    (Measurement.date <= end_date)).first()

    session.close()

    #Return data
    temp_stats = []
    stats_dict = {}
    stats_dict['Min Temp'] = results.min_temp
    stats_dict['Max Temp'] = results.max_temp
    stats_dict['Avg Temp'] = results.avg_temp
    temp_stats.append(stats_dict)

    return jsonify(temp_stats)


@app.route("/api/v1.0/<start_date>")
def date_greater_temps(start_date):

    """Return Temperature stats for date range"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query Temp stats
    results = session.query(Measurement,
                            func.min(Measurement.tobs).label('min_temp'), 
                            func.max(Measurement.tobs).label('max_temp'),
                            func.avg(Measurement.tobs).label('avg_temp')).\
                            filter(Measurement.date >= start_date).first()

    session.close()

    #Return data
    temp_stats = []
    stats_dict = {}
    stats_dict['Min Temp'] = results.min_temp
    stats_dict['Max Temp'] = results.max_temp
    stats_dict['Avg Temp'] = results.avg_temp
    temp_stats.append(stats_dict)

    return jsonify(temp_stats)



if __name__ == '__main__':
    app.run(debug=True)
