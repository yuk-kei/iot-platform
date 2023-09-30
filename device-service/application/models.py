from . import db

"""
Models Module

This module defines the data structures (models) used in the application's database layer.
Each class typically corresponds to a table in the database, encapsulating the fields and relationships 
of that table. The models provide a framework for ORM (Object-Relational Mapping) operations, enabling
easy interactions between the application's business logic and the database.

Current Models:
    - Device: Represents a device entity with attributes such as name, type, location, etc.

Expected Additions:
    More models are anticipated to be added to this module as the application expands. These may include
    models for users, transactions, logs, etc.

"""


class Device(db.Model):
    """
    A Device class that represents devices in the database.

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

    Methods:
        __repr__(): Returns a string representation of the Device object.
    """
    __tablename__ = 'devices'
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(32), unique=True)
    category = db.Column(db.String(32))
    type = db.Column(db.String(64))
    location = db.Column(db.String(64))
    status = db.Column(db.String(32))
    ip_address = db.Column(db.String(128))
    port = db.Column(db.Integer)

    def __repr__(self):
        return '<Device %r>' % self.name
