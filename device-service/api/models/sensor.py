from .. import db

"""
Models Module

Current Models:
    - 

Expected Additions:
    

"""


class Sensor(db.Model):
    """
    A Sensor class that represents sensors in the database.

    Attributes:
        __tablename__ (str): Name of the table in the database.
        id (str): Unique identifier for the device.
        name (str): Name of the device.
        category (str): Category/type of the device.
        type (str): Specific type or model of the device.
        location (str): Physical or logical location of the device.
        status (str): Current status of the device (e.g., online, offline, maintenance).
        ip_address (str): IP address assigned to the device.
        port (int): Port number used for communicating with the device.

        sensor_id	int Auto Increment +
        sensor_uuid	char(36) NULL +
        name	varchar(255) NULL +
        category	varchar(255) NULL +
        sensor_type	varchar(255) NULL +
        sensor_vendor	varchar(255) NULL +
        vendor_pid	varchar(255) NULL +
        chip	varchar(255) NULL +
        rpi_id	int NULL
        is_key_sensor	tinyint NULL [0]

    Methods:
        __repr__(): Returns a string representation of the Device object.
    """
    __tablename__ = 'sensors'
    sensor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_uuid = db.Column(db.CHAR(36), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)
    sensor_type = db.Column(db.String(255), nullable=True)
    sensor_vendor = db.Column(db.String(255), nullable=True)
    vendor_pid = db.Column(db.String(255), nullable=True)
    chip = db.Column(db.String(255), nullable=True)
    rpi_id = db.Column(db.Integer, nullable=True)
    is_key_sensor = db.Column(db.Integer, nullable=True, default=0)

    def __repr__(self):
        return '<Sensor %r>' % self.name
