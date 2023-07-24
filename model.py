import time, uuid

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(32))
    category = db.Column(db.String(32))
    type = db.Column(db.String(64))
    location = db.Column(db.String(64))
    status = db.Column(db.String(32))
    ip_address = db.Column(db.String(128))
    port = db.Column(db.Integer)

    def __repr__(self):
        return '<Device %r>' % self.name


