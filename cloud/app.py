#!/usr/bin/env python3

from ast import literal_eval
import datetime
from flask import Flask, flash, render_template, request   # jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
import jwt

from config import Config

appname = "Shopmaker"
app = Flask(__name__)
myconfig = Config
app.config.from_object(myconfig)
Bootstrap(app)

# db creation
db = SQLAlchemy(app)

migrate = Migrate()
migrate.init_app(app, db)

from models import Sensor, Sensorfeed, Actuator, Customer
from customerlogic import getCustomerNumberInTimeInterval, getCurrentMainAgeAndGender


def queryForSensor(sensorid, bridgeid):
    sensor = Sensor.query.filter_by(local_id=sensorid, bridge_id=bridgeid).first_or_404()

    if not sensor:
        print("Warning: Sensor not found with id: ", sensorid)
        return "Given id for sensor not in database", 400, None
    return "Ok", 200, sensor


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


def getCustomerNumber():
    currentTime = datetime.datetime.utcnow()
    oneHourAgo = currentTime - datetime.timedelta(days=1)
    customerNumber = db.session.query(Customer).filter(
        Customer.timestamp > oneHourAgo).all().count(Customer.id)

    return customerNumber


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return {'message': 'a valid token is missing'}

        try:
            data = jwt.decode(token, app.config['TOKEN_SECRET_KEY'], algorithms=["HS256"])
            if not str(data['public_id']) in app.config['TOKEN_BRIDGE_IDS']:
                raise Exception('Public id not in expected tokens')
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            return {'message': 'token is invalid'}
        return f()
    return decorator


@app.errorhandler(404)
def page_not_found(error):
    return 'Error', 404


"""UI Paths"""


@app.route('/')
def overview():
    try:
        deviceNumber = Sensor.query.count() + Actuator.query.count()
    except:
        deviceNumber = 0
    bridgeNumber = 1    # TODO: query correctly DB
    return render_template(
        'index.html',
        devices=deviceNumber,
        bridges=bridgeNumber,
        customers=getCustomerNumberInTimeInterval(datetime.timedelta(days=1)))


@app.route('/sensors')
def sensorOverview():
    sensors = Sensor.query.all()
    typedictionary = collectDeviceMetrics(sensors)
    types = [key for key in typedictionary.keys()]
    values = [value for value in typedictionary.values()]
    bridgedictionary = collectBridgeMetrics(sensors)
    bridges = [int(key) for key in bridgedictionary.keys()]
    numbers = [value for value in bridgedictionary.values()]
    return render_template('sensoroverview.html',
                           devices=sensors,
                           devtypes=types,
                           values=values,
                           bridges=bridges,
                           numbers=numbers,
                           devicetype='Sensors')


@app.route('/actuators')
def actuatorOverview():
    actuators = Actuator.query.all()
    typedictionary = collectDeviceMetrics(actuators)
    types = [key for key in typedictionary.keys()]
    values = [value for value in typedictionary.values()]
    bridgedictionary = collectBridgeMetrics(actuators)
    bridges = [key for key in bridgedictionary.keys()]
    numbers = [value for value in bridgedictionary.values()]
    return render_template('actuatoroverview.html',
                           devices=actuators,
                           devtypes=types,
                           values=values,
                           bridges=bridges,
                           numbers=numbers,
                           devicetype='Actuators')


@app.route('/actuating/<int:actuator_id>')
def actuating(actuator_id):
    actuator = Actuator.query.filter_by(id=actuator_id).first_or_404()
    return render_template('actuating.html', actuator=actuator)


@app.route('/actuate/<int:actuator_id>', methods=['POST'])
def actuate(actuator_id):
    value = request.form['value']
    # in order to not try to send things to the bridge where no actuator exists
    actuator = Actuator.query.filter_by(id=actuator_id).first_or_404()
    if not value:
        flash('Nothing sent as value was empty :(')
        return render_template('actuating.html', actuator=actuator)
    actuator.next_value = value
    db.session.commit()
    flash('Success: Value will be send to actuator on next update!')
    return render_template('actuating.html', actuator=actuator)


@app.route('/test')
def test():
    # add initial sensor
    sensor = Sensor(bridge_id=1, datatype="integer")
    actuator = Actuator(bridge_id=1, datatype="integer")
    db.session.add(sensor)
    db.session.add(actuator)
    db.session.commit()
    return str(sensor.id)


@app.route('/about')
def about():
    return render_template('about.html')


"""REST API for Bridge"""


@app.route('/initializebridge', methods=['POST'])
@token_required
def initializeBridge():
    # delete all objects saved for this bridge so far since it was turned of in between and will start initializing now
    json_data = request.get_json()
    bridgeid = json_data['bridgeid']
    print(bridgeid)

    # TODO: change database that all associated sensorfeeds to the deleted sensors also get deleted

    sensors = Sensor.query.filter_by(bridge_id=1)
    for sensor in sensors:
        sensorfeeds = Sensorfeed.__table__.delete().where(Sensorfeed.sensor_id == sensor.id)
        db.session.execute(sensorfeeds)
    deleted_sensors = Sensor.__table__.delete().where(Sensor.bridge_id == bridgeid)
    db.session.execute(deleted_sensors)

    deleted_actuators = Actuator.__table__.delete().where(Actuator.bridge_id == bridgeid)
    db.session.execute(deleted_actuators)

    db.session.commit()
    return '200'


@app.route('/adddevice', methods=['POST'])
@token_required
def addDevice():
    json_data = request.get_json()
    device_id = 0
    bridgeid = json_data['bridgeid']

    if json_data['sensor'] == 'True':
        if Sensor.query.filter_by(bridge_id=bridgeid).count() == 0:
            # needed for first sensor
            sensor = Sensor(bridge_id=bridgeid, local_id=0, datatype=json_data['datatype'])
            sensor.addToDatabase()
        else:
            last_sensor = Sensor.query.filter_by(bridge_id=bridgeid).order_by(
                Sensor.local_id.desc()).limit(1).first_or_404()
            print(last_sensor)
            sensor = Sensor(bridge_id=bridgeid, local_id=(last_sensor.local_id + 1), datatype=json_data['datatype'])
            sensor.addToDatabase()
            device_id = sensor.local_id
    else:
        if Actuator.query.filter_by(bridge_id=bridgeid).count() == 0:
            actuator = Actuator(bridge_id=bridgeid, local_id=0, datatype=json_data['datatype'])
            actuator.addToDatabase()
        else:
            last_actuator = Actuator.query.filter_by(bridge_id=bridgeid).order_by(
                Actuator.local_id.desc()).limit(1).first_or_404()
            actuator = Actuator(bridge_id=bridgeid, local_id=(
                last_actuator.local_id + 1), datatype=json_data['datatype'])
            actuator.addToDatabase()
            device_id = actuator.local_id

    return str(device_id)


@app.route('/addvalue', methods=['POST'])
@token_required
def addInlist():
    json_data = request.get_json()

    bridgeid = int(json_data['bridgeid'])
    sensorid = int(json_data['sensorid'])
    text, statuscode, sensor = queryForSensor(sensorid, bridgeid)

    if statuscode == 400:
        return text, statuscode

    data = json_data['data']

    sf = Sensorfeed(sensor_id=sensor.id, value=data)
    sf.addToDatabase()
    print("for bridge: ", bridgeid, "and for sensor: ", sensorid, "added value: ", data)

    return str(0)    # function must return something that is not an integer


@app.route('/getNewValues', methods=['POST'])
@token_required
def getNewValues():
    json_data = request.get_json()
    print(json_data)

    bridgeid = json_data['bridgeid']

    actuator_number = int(json_data['actuator_num'])
    actuator_list = json_data['actuators']

    json_answer = {}
    print("number of actuators:", actuator_number)

    age, gender = getCurrentMainAgeAndGender()

    for i in range(actuator_number):
        actuator = Actuator.query.filter_by(bridge_id=bridgeid, local_id=actuator_list[i]).first_or_404()
        if actuator.datatype == 'heater':
            tempSensor = Sensor.query.filter_by(datatype='temperature').first_or_404()
            tempSensorFeed = Sensorfeed.query.filter_by(sensor_id=tempSensor.id).first_or_404()
            if float(tempSensorFeed.value) < 20 and gender == 'F':
                value = "1"
            else:
                value = "0"
        elif actuator.next_value != "None":
            value = actuator.next_value
            actuator.next_value = "None"
        else:
            value = "2"
        actuator.last_value = str(value)
        json_answer[str(actuator.local_id)] = value

    db.session.commit()
    print(json_answer)
    return json_answer


@app.route('/addpredicted', methods=['POST'])
@token_required
def addPredictedValues():
    # getting the predicted ages and genders from edge computing via image captioning
    json_data = request.get_json()
    bridgeid = json_data['bridgeid']

    text, statuscode, sensor = queryForSensor(int(json_data['sensorid']), bridgeid)

    if statuscode == 400:
        return text, statuscode

    data_list = json_data['data']

    # Expecting data in the format: {..., data: {'Gender' : 'M', 'Age' : '(23, 32)'}}

    print(data_list)
    gender = data_list['Gender']
    age_tuple = literal_eval(data_list['Age'])
    age = (age_tuple[0] + age_tuple[1]) / 2
    person = Customer(gender=gender, age=age)
    person.addToDatabase()

    return str(0)


if __name__ == '__main__':
    app.run()
