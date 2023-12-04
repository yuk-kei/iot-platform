from .. import db

"""
Models Module

Current Models:
    - 

Expected Additions:


"""


class Lab(db.Model):
   """
   A Lab class that represents labs in the database.

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

      lab_id	int Auto Increment
      name	varchar(255) NULL
      type	varchar(255) NULL

   Methods:
       __repr__(): Returns a string representation of the Lab object.
   """
   __tablename__ = 'labs'
   lab_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
   name = db.Column(db.String(255), nullable=True)
   type = db.Column(db.String(255), nullable=True)

   def __repr__(self):
      return '<Lab %r>' % self.name
