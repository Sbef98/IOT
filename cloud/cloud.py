#!/usr/bin/env python3

from config import Config
from flask import Flask
from flask import render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

appname = "Shopmaker"
app = Flask(appname)
myconfig = Config
# TODO: check why the url on which we are running is not 127.0.0.1
app.config.from_object(myconfig)

# db creation
db = SQLAlchemy(app)

class Sensorfeed(db.Model):
    id = db.Column('sensorid', db.Integer, primary_key = True)
    value = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False,  default=datetime.utcnow)

    def __init__(self, sensorid, value):
        self.value = value

    def addToDatabase(self):
        db.session.add(self)
        db.session.commit()

@app.errorhandler(404)
def page_not_found(error):
    return 'Error', 404

@app.route('/')
def test():
    return render_template('index.html')

@app.route('/addvalue', methods=['POST'])
def addinlist():
    json_data = request.get_json()

    sensorid = json_data['sensorid']
    datasize = int(json_data['datasize'])
    data_list = json_data['data']

    for i in range(datasize):
        print(i)
        sf = Sensorfeed(sensorid, data_list[i])
        sf.addToDatabase()
        print("added value: ", data_list[i], "for sensor:", sensorid)
        
    return str(0) # function must return something that is not an integer

if __name__ == '__main__':

    if True:  # first time (?)
        db.create_all()

    port = 80
    interface = '0.0.0.0'
    app.run(host=interface,port=port, debug=True)