#!/usr/bin/env python3

from config import Config
from datetime import datetime
from flask import Flask
from flask import render_template, request
from flask_sqlalchemy import SQLAlchemy

appname = "Shopmaker"
app = Flask(appname)
myconfig = Config
# TODO: check why the url on which we are running is not 127.0.0.1
app.config.from_object(myconfig)

# db creation
db = SQLAlchemy(app)

class Actuator(db.Model):
    __tablename__ = 'actuator'
    id = db.Column('id', db.Integer, primary_key = True)
    bridge_id = db.Column(db.Integer, nullable = False)
    datatype = db.Column(db.String(100), nullable = False)

    def addToDatabase(self):
        db.session.add(self)
        db.session.commit()

class Sensor(db.Model):
    __tablename__ = 'sensor'
    id = db.Column('id', db.Integer, primary_key = True)
    bridge_id = db.Column(db.Integer, nullable = False)
    datatype = db.Column(db.String(100), nullable = False)

    def addToDatabase(self):
        db.session.add(self)
        db.session.commit()

class Sensorfeed(db.Model):
    __tablename__ = 'sensorfeed'
    id = db.Column('feedid', db.Integer, primary_key = True)
    value = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False,  default=datetime.utcnow)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)
    sensor =  db.relationship('Sensor', backref = db.backref('sensor_id'), 
        foreign_keys = [sensor_id], lazy = True)

    def addToDatabase(self):
        db.session.add(self)
        db.session.commit()

@app.errorhandler(404)
def page_not_found(error):
    return 'Error', 404

@app.route('/')
def test():
    # add initial sensor
    sensor = Actuator(bridge_id = 1, datatype = "string")
    db.session.add(sensor)   
    db.session.commit()
    return str(sensor.id)

@app.route('/adddevice', methods=['POST'])
def addDevice():
    json_data = request.get_json()
    device_id = 0

    if (json_data['sensor'] == 'True'):
        sensor = Sensor(bridge_id = json_data['bridge'], datatype=json_data['datatype'])
        sensor.addToDatabase()
        device_id = sensor.id
    else:
        actuator = Actuator(bridge_id = json_data['bridge'], datatype=json_data['datatype'])
        actuator.addToDatabase()
        device_id = actuator.id

    return str(device_id)

@app.route('/addvalue', methods=['POST'])
def addinlist():
    json_data = request.get_json()

    sensorid = int(json_data['sensorid'])
    sensor = Sensor.query.get(sensorid)

    if (not sensor):
        print("Warning: Sensor not found with id: ", sensorid)
        return "Given id for sensor not in database", 400

    datasize = int(json_data['datasize'])
    data_list = json_data['data']

    for i in range(datasize):
        sf = Sensorfeed(sensor_id=sensor.id, value=data_list[i])
        sf.addToDatabase()
        print("added value: ", data_list[i], "for sensor:", sensorid)

    return str(0) # function must return something that is not an integer

@app.route('/getNewValues', methods=['POST'])
def getNewValues():
    json_data = request.get_json()

    actuator_number = json_data['actuator_num']
    actuator_list = json_data['actuators']

    json_answer = {}

    for i in range(actuator_number):
        actuator = Actuator.query.get(actuator_list[i])
        if (actuator.datatype == 'string'):
            json_answer[str(actuator.id)] = "hello"
    return json_answer

if __name__ == '__main__':

    if True:  # first time (?)
        db.create_all()

    port = 8000
    interface = '0.0.0.0'
    app.run(host=interface,port=port, debug=True)