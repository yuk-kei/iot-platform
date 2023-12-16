from .. import db


class Machine(db.Model):
    """Machine Model

    Arguments:
        db {SQLAlchemy} -- SQLAlchemy Object for database interaction

    machine_id {Integer} -- Unique ID for each machine
    machine_uuid {CHAR(36)} -- UUID for each machine
    name {String(255)} -- Name of the machine
    type {String(255)} -- Type of the machine
    vendor {String(255)} -- Vendor of the machine
    year {Integer} -- Year the machine was made
    lab_id {Integer} -- ID of the lab the machine is in
    """

    __tablename__ = 'machine'
    machine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_uuid = db.Column(db.CHAR(36), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(255), nullable=True)
    vendor = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.id'), nullable=True)

    def __repr__(self):
        return '<Machine %r>' % self.name

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if getattr(self, c.name) is not None}


class MachineSensorMap(db.Model):
    """Machine Sensor Map Model

    Arguments:
        db {SQLAlchemy} -- SQLAlchemy Object for database interaction

    machine_sensor_map_id {Integer} -- Unique ID for each machine sensor map
    machine_id {Integer} -- ID of the machine
    sensor_id {Integer} -- ID of the sensor
    """

    __tablename__ = 'machine_sensor_mapping'
    map_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=True)
    is_key_sensor = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return '<MachineSensorMap %r>' % self.map_id

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if getattr(self, c.name) is not None}
