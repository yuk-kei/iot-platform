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
