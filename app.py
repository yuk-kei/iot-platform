from flask import Flask
from model import db, Device

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


from route import *


# # Create the application context
with app.app_context():
    # Create database tables
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9002)
