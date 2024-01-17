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
    machine_id = db.Column('machine_id', db.Integer, primary_key=True, autoincrement=True)
    machine_uuid = db.Column(db.CHAR(36), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(255), nullable=True)
    vendor = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    lab_name = db.Column(db.String(255), db.ForeignKey('lab.name'), nullable=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.lab_id'), nullable=True)

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
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.machine_id'), nullable=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.sensor_id'), nullable=True)
    machine_name = db.Column(db.String(255), db.ForeignKey('machine.name'), nullable=True)
    sensor_name = db.Column(db.String(255), db.ForeignKey('sensor.name'), nullable=True)
    is_key_sensor = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<MachineSensorMap %r>' % self.map_id

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if getattr(self, c.name) is not None}


class MachineResult(db.Model):
    __tablename__ = 'machine_result'
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.machine_id'), nullable=True)
    machine_name = db.Column(db.String(255), db.ForeignKey('machine.name'), nullable=True)
    machine_status = db.Column(db.String(255), nullable=True)
    material_status = db.Column(db.String(255), nullable=True)
    operator_status = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<MachineResult {self.machine_name}>'

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if getattr(self, c.name) is not None}


class MachineOverview(db.Model):
    __tablename__ = 'machine_overview'
    overview_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.machine_id'), nullable=True)
    machine_name = db.Column(db.String(255), db.ForeignKey('machine.name'), nullable=True)
    summary_info = db.Column(db.String(255), nullable=True)
    last_update = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<MachineOverview {self.machine_name}>'

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if getattr(self, c.name) is not None}


class Rpi(db.Model):
    __tablename__ = 'rpi'
    rpi_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rpi_uuid = db.Column(db.CHAR(36), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    rpi_type = db.Column(db.String(255), nullable=True)
    ip = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.machine_id'), nullable=True)
    machine_name = db.Column(db.String(255), db.ForeignKey('machine.name'), nullable=True)
    comment = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Rpi {self.name}>'

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if getattr(self, c.name) is not None}
