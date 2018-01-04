# import dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify
import datetime

# reflect database tables (Measurment & Station) into classes
engine = create_engine("sqlite:///hawaii.sqlite", echo=False)

Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# get datetime to be used within functions
current_datetime = datetime.datetime.now()
year = datetime.timedelta(days=365)
year_ago = current_datetime - year
today = current_datetime.strftime('%Y-%m-%d')

# define method for temperature calculations
def calc_temps(start_date, end_date=today):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# create app
app = Flask(__name__)

# define routes and functions
@app.route("/")
def home():
    return (
        f"<br/>"
        f"Welcome to the Hawaiian Weather Center!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"Returns precipitation data for the previous year<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"Returns a list of weather stations<br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"Returns observed temperatures from the previous year<br/><br/>"
        f"/api/v1.0/[start]/[end]<br/>"
        f"Returns the minimum, average, and maximum temperatures for a given date range<br/>"
        f"If no end date is provided, all dates after the start date will be included<br/>"        
    )

# retrieve precipitation data for previous year
@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > year_ago).all()
    recent_prcp_json = jsonify(dict(recent_prcp))
    return recent_prcp_json

# /api/v1.0/stations
# Return a json list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(Station.station, Station.name).all()
    station_list_json = jsonify(station_list)
    return station_list_json

# /api/v1.0/tobs
# Return a json list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    recent_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > year_ago).all()
    recent_tobs_json = jsonify(dict(recent_tobs))
    return recent_tobs_json

# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>")
def temp_info_open_ended(start):
    temp_data = calc_temps(start)
    min_temp, avg_temp, max_temp = temp_data[0]
    temp_results = {
        "minimum temperature":min_temp,
        "average temperature":avg_temp,
        "maximum temperature":max_temp
    }
    temp_results_json = jsonify(temp_results)
    return temp_results_json


@app.route("/api/v1.0/<start>/<end>")
def temp_info(start, end):
    temp_data = calc_temps(start, end)
    min_temp, avg_temp, max_temp = temp_data[0]
    temp_results = {
        "minimum temperature":min_temp,
        "average temperature":avg_temp,
        "maximum temperature":max_temp
    }
    temp_results_json = jsonify(temp_results)
    return temp_results_json

# define main behavior
if __name__ == "__main__":
    app.run(debug=True)