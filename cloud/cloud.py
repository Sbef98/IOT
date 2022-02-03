#!/usr/bin/env python3

from datetime import datetime

from config import Config
from flask import render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask
from flask import render_template, request
from flask_sqlalchemy import SQLAlchemy

appname = "Shopmaker"
app = Flask(appname)
myconfig = Config
app.config.from_object(myconfig)
Bootstrap(app)

# db creation
db = SQLAlchemy(app)

class Actuator(db.Model):
    __tablename__ = 'actuator'
    id = db.Column('id', db.Integer, primary_key = True)
    bridge_id = db.Column(db.Integer, nullable = False)
    local_id = db.Column(db.Integer, nullable = False) # keys need to be under 255 in the current protocol
    datatype = db.Column(db.String(100), nullable = False)
    # both stored as string in order to all possible datatypes
    last_value = db.Column(db.String(100), nullable = True)
    next_value = db.Column(db.String(100), nullable = True)

    def addToDatabase(self):
        db.session.add(self)
        db.session.commit()

class Sensor(db.Model):
    __tablename__ = 'sensor'
    id = db.Column('id', db.Integer, primary_key = True)
    bridge_id = db.Column(db.Integer, nullable = False)
    local_id = db.Column(db.Integer, nullable = False) # keys need to be under 255 in the current protocol
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
    sensor =  db.relationship('Sensor', backref = db.backref('sensor_id', cascade='all, delete-orphan'), 
        foreign_keys = [sensor_id])

    def addToDatabase(self):
        db.session.add(self)
        db.session.commit()

def collectDeviceMetrics(devices):
    typedict = {}
    for device in devices:
        if device.datatype in typedict:
            typedict[device.datatype] += 1
        else:
            typedict[device.datatype] = 1
    return typedict

def collectBridgeMetrics(devices):
    bridgedict = {}
    for device in devices:
        if device.bridge_id in bridgedict:
            bridgedict[device.bridge_id] += 1
        else:
            bridgedict[device.bridge_id] = 1
    return bridgedict

@app.errorhandler(404)
def page_not_found(error):
    return 'Error', 404

@app.route('/')
def overview():
    return render_template('index.html')

@app.route('/sensors')
def sensoroverview():
    sensors = Sensor.query.all()
    typedictionary = collectDeviceMetrics(sensors)
    types = [key for key in typedictionary.keys()]
    values = [value for value in typedictionary.values()]
    bridgedictionary = collectBridgeMetrics(sensors)
    bridges = [int(key) for key in bridgedictionary.keys()]
    numbers = [value for value in bridgedictionary.values()]
    return render_template('deviceoverview.html', devices = sensors, devtypes = types, values = values, bridges = bridges, numbers = numbers, devicetype = 'Sensors')

@app.route('/actuators')
def actuatoroverview():
    actuators = Actuator.query.all()
    typedictionary = collectDeviceMetrics(actuators)
    types = [key for key in typedictionary.keys()]
    values = [value for value in typedictionary.values()]
    bridgedictionary = collectBridgeMetrics(actuators)
    bridges = [key for key in bridgedictionary.keys()]
    numbers = [value for value in bridgedictionary.values()]
    return render_template('deviceoverview.html', devices = actuators, devtypes = types, values = values, bridges = bridges, numbers = numbers, devicetype = 'Actuators')

@app.route('/test')
def test():
    # add initial sensor
    sensor = Sensor(bridge_id = 1, datatype = "integer")
    actuator = Actuator(bridge_id = 1, datatype = "integer")
    db.session.add(sensor)
    db.session.add(actuator)   
    db.session.commit()
    return str(sensor.id)

@app.route('/initializebridge', methods=['POST'])
def initializeBridge():
    # delete all objects saved for this bridge so far since it was turned of in between and will start initializing now
    json_data = request.get_json()
    bridgeid = json_data['bridgeid']

    # TODO: change database that all associated sensorfeeds to the deleted sensors also get deleted

    deleted_sensors = Sensor.__table__.delete().where(Sensor.bridge_id == bridgeid)
    db.session.execute(deleted_sensors)

    deleted_actuators = Actuator.__table__.delete().where(Actuator.bridge_id == bridgeid)
    db.session.execute(deleted_actuators)

    db.session.commit()
    return '200'

@app.route('/adddevice', methods=['POST'])
def addDevice():
    json_data = request.get_json()
    device_id = 0
    bridgeid = json_data['bridgeid']

    if (json_data['sensor'] == 'True'):
        if (Sensor.query.filter_by(bridge_id=bridgeid).count() == 0):
            # needed for first sensor
            sensor = Sensor(bridge_id=bridgeid, local_id=0, datatype=json_data['datatype'])
            sensor.addToDatabase()
        else:
            last_sensor = Sensor.query.filter_by(bridge_id=bridgeid).order_by(Sensor.local_id.desc()).limit(1).first_or_404()
            print(last_sensor)
            sensor = Sensor(bridge_id=bridgeid, local_id=(last_sensor.local_id + 1), datatype=json_data['datatype'])
            sensor.addToDatabase()
            device_id = sensor.local_id
    else:
        if(Actuator.query.filter_by(bridge_id=bridgeid).count() == 0):
            actuator = Actuator(bridge_id=bridgeid, local_id=0, datatype=json_data['datatype'])
            actuator.addToDatabase()
        else:
            last_actuator = Actuator.query.filter_by(bridge_id=bridgeid).order_by(Actuator.local_id.desc()).limit(1).first_or_404()
            actuator = Actuator(bridge_id=bridgeid, local_id=(last_actuator.local_id + 1), datatype=json_data['datatype'])
            actuator.addToDatabase()
            device_id = actuator.local_id

    return str(device_id)

@app.route('/addvalue', methods=['POST'])
def addinlist():
    json_data = request.get_json()

    bridgeid = int(json_data['bridgeid'])
    sensorid = int(json_data['sensorid'])
    sensor = Sensor.query.filter_by(local_id=sensorid, bridge_id=bridgeid).first_or_404()

    if (not sensor):
        print("Warning: Sensor not found with id: ", sensorid)
        return "Given id for sensor not in database", 400

    datasize = int(json_data['datasize'])
    data_list = json_data['data']

    for i in range(datasize):
        sf = Sensorfeed(sensor_id=sensor.id, value=data_list[i])
        sf.addToDatabase()
        print("for bridge: ", bridgeid, "and for sensor: ", sensorid, "added value: ", data_list[i])

    return str(0) # function must return something that is not an integer

@app.route('/getNewValues', methods=['POST'])
def getNewValues():
    json_data = request.get_json()
    print(json_data)

    bridgeid = json_data['bridgeid']

    actuator_number = int(json_data['actuator_num'])
    actuator_list = json_data['actuators']

    json_answer = {}
    print("number of actuators:", actuator_number)

    for i in range(actuator_number):
        actuator = Actuator.query.filter_by(bridge_id=bridgeid, local_actuator_id=actuator_list[i]).first_or_404()
        if(actuator.next_value == "None"):
            value = actuator.next_value
            actuator.next_value = "None"
        elif (actuator.datatype == 'string'):
            value ="hello"
        else:
            value = "2"
        actuator.last_value = str(value)
        json_answer[str(actuator.id)] = value
        
    db.session.commit()
    print(json_answer)
    return json_answer

if __name__ == '__main__':

    if True:  #create database on first turn on
        db.create_all()

    port = 8000
    interface = '0.0.0.0'
    app.run(host=interface,port=port, debug=True)
