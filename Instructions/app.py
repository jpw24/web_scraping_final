import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import scrape_mars
from flask import Flask, jsonify, render_template, redirect, request
from flask_pymongo import PyMongo

########################################
app = Flask(__name__)

mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

#################################################
# Flask Routes
#################################################


@app.route("/")
def home():
    # Find one record of data from the mongo database
    mars_mongo_data = mongo.db.collection.find_one()
    #print(mars_mongo_data)
    # Return template and m
    return render_template("index.html", mars=mars_mongo_data)


@app.route("/scrape")
def scrape():
    # Run the scrape function
    mars_data = scrape_mars.scrape_info()

    # Update the Mongo database using update and upsert=True
    mongo.db.collection.update({}, mars_data, upsert=True)

    # Redirect back to home page
    return redirect("/")

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    app.run(debug=True)