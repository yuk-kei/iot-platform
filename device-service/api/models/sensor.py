from .. import db


class Sensor(db.Model):
    """
    A Sensor class that represents sensors in the database.

    Attributes:
        __tablename__ (str): Name of the table in the database.
        sensor_id (str): Unique identifier for the device.
        name (str): Name of the device.
        category (str): Category of the device.
        sensor_type (str): Type of the device.
        sensor_vendor (str): Vendor of the device.
        vendor_pid (str): Vendor PID of the device.
        chip (str): Chip of the device.
        rpi_id (str): Raspberry Pi ID of the device.

    Methods:
        __repr__(): Returns a string representation of the Device object.
    """
    __tablename__ = 'sensor'
    sensor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_uuid = db.Column(db.CHAR(36), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)
    frequency = db.Column(db.Float, nullable=True)
    sensor_type = db.Column(db.String(255), nullable=True)
    sensor_vendor = db.Column(db.String(255), nullable=True)
    vendor_pid = db.Column(db.String(255), nullable=True)
    chip = db.Column(db.String(255), nullable=True)
    rpi_name = db.Column(db.String(255), db.ForeignKey('rpis.name'), nullable=True)
    rpi_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Sensor %r>' % self.name

    def to_dict(self):
        """
        Returns a dictionary representation of the Sensor object.

        Returns:
            dict: Dictionary representation of the Sensor object.
        """

        return {c.name: getattr(self, c.name) for c in self.__table__.columns if getattr(self, c.name) is not None}


class Attribute(db.Model):
    """
    A Attributes class that represents attributes in the database.

    Attributes:
        __tablename__ (str): Name of the table in the database.
        attribute_id (str): Unique identifier for the attribute.
        sensor_id (str): Unique identifier for the device.
        attribute (str): Name of the attribute.
        is_key_attribute (str): Whether the attribute is a key attribute.

    Methods:
        __repr__(): Returns a string representation of the Attribute object.

    """
    __tablename__ = 'sensor_attribute'
    attribute_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.sensor_id'))
    sensor_name = db.Column(db.String(255), db.ForeignKey('sensor.name'))
    attribute = db.Column(db.String(255), nullable=True)
    is_key_attribute = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Attributes %r>' % self.name

    def to_dict(self):
        """
        Returns a dictionary representation of the Attributes object.

        Returns:
            dict: Dictionary representation of the Attributes object.
        """

        return {c.name: getattr(self, c.name) for c in self.__table__.columns if getattr(self, c.name) is not None}


class Url(db.Model):
    """
    A Url_list class that represents url_list in the database.

    Attributes:
        __tablename__ (str): Name of the table in the database.
        url_id (str): Unique identifier for the url.
        sensor_id (str): Unique identifier for the device.
        url (str): Url of the device.

    Methods:
        __repr__(): Returns a string representation of the Url_list object.

    """
    __tablename__ = 'sensor_url'
    url_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.sensor_id'))
    sensor_name = db.Column(db.String(255), db.ForeignKey('sensor.name'))
    url = db.Column(db.String(255), nullable=True)
    url_type = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return '<Url_list %r>' % self.name

    def get_url(self):
        return self.url

    def to_dict(self):
        """
        Returns a dictionary representation of the Url_list object.

        Returns:
            dict: Dictionary representation of the Url_list object.
        """

        return {c.name: getattr(self, c.name) for c in self.__table__.columns if getattr(self, c.name) is not None}
