from .. import db

"""
Models Module

Current Models:
    - 

Expected Additions:


"""


class Machine(db.Model):
   """
   A Machine class that represents sensors in the database.

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

      machine_id	int Auto Increment
      machine_uuid	char(36) NULL
      name	varchar(255) NULL
      type	varchar(255) NULL
      model	varchar(255) NULL
      vendor	varchar(255) NULL
      year	year NULL
      lab_id	int NULL

   Methods:
       __repr__(): Returns a string representation of the Machine object.
   """
   __tablename__ = 'machines'
   machine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   machine_uuid = db.Column(db.CHAR(36), nullable=True)
   name = db.Column(db.String(255), nullable=True)
   type = db.Column(db.String(255), nullable=True)
   vendor = db.Column(db.String(255), nullable=True)
   year = db.Column(db.Integer, nullable=True)
   lab_id = db.Column(db.Integer, nullable=True)

   def __repr__(self):
      return '<Machine %r>' % self.name
