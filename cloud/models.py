from manage import db
from datetime import datetime

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
