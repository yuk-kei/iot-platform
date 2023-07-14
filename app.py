import os

from flask import Flask
from model import db, Device

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DEV_DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)
from route import *


# Create the application context
with app.app_context():
    # Create database tables
    db.create_all()

if __name__ == '__main__':
    app.run(port=9002)
