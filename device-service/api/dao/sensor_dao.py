import time
import uuid

from ..models.sensor import Sensor, Attribute, Url
from ..models.machine import Machine, MachineSensorMap, Rpi
from .. import db


class SensorDAO:

    @staticmethod
    def create(sensor_info, rpi_name=None, machine_names=None, attributes=None, urls=None):
        # Assuming sensor_info is a dictionary containing sensor details

        new_sensor = Sensor(
            sensor_uuid=next_short_id(),
            name=sensor_info.get('name'),
            frequency=sensor_info.get('frequency', None),
            category=sensor_info.get('category', None),
            sensor_type=sensor_info.get('sensor_type', None),
            sensor_vendor=sensor_info.get('sensor_vendor', None),
            vendor_pid=sensor_info.get('vendor_id', None),
            chip=sensor_info.get('chip', None),
        )

        if rpi_name:
            rpi = Rpi.query.filter_by(name=rpi_name).first()
            if rpi:
                new_sensor.rpi_id = rpi.rpi_id

        db.session.add(new_sensor)
        db.session.flush()  # Flush to get the new_sensor ID before commit

        # Associate with Machines

        if machine_names:
            for machine_name in machine_names:
                machine = Machine.query.filter_by(name=machine_name).first()
                if machine:
                    machine_sensor_map = MachineSensorMap(
                        machine_id=machine.machine_id,
                        sensor_id=new_sensor.sensor_id,
                        machine_name=machine_name,
                        sensor_name=new_sensor.name,
                        is_key_sensor=sensor_info.get('is_key_sensor')
                    )
                    db.session.add(machine_sensor_map)

        # Handle Attributes
        if attributes:
            for attr_data in attributes:
                attribute = Attribute(
                    sensor_id=new_sensor.sensor_id,
                    sensor_name=new_sensor.name,
                    attribute=attr_data.get('attribute'),
                    is_key_attribute=attr_data.get('is_key_attribute')
                )
                db.session.add(attribute)

        # Handle URLs
        if urls:
            for url_data in urls:
                url = Url(
                    sensor_id=new_sensor.sensor_id,
                    sensor_name=new_sensor.name,
                    url=url_data.get('url'),
                    url_type=url_data.get('url_type')
                )
                db.session.add(url)

        db.session.commit()
        return new_sensor

    @staticmethod
    def get_all(page=1, per_page=30):
        if page is None:
            return Sensor.query.all()
        else:
            paginated = Sensor.query.paginate(page=page, per_page=per_page, error_out=False)
            return paginated.items, paginated.total

    @staticmethod
    def get_single(sensor_identifier):
        if isinstance(sensor_identifier, int):
            return Sensor.query.get(sensor_identifier)
        elif isinstance(sensor_identifier, str):
            return Sensor.query.filter_by(name=sensor_identifier).first()

    @staticmethod
    def get_all_attributes(sensor_id, page=None, per_page=30):
        if page is None:
            return Attribute.query.get(sensor_id).attributes
        else:
            paginated = (Attribute.query(sensor_id).paginate(page=page, per_page=per_page, error_out=False))
            return paginated.items, paginated.pages, paginated.total

    @staticmethod
    def get_key_attribute(sensor_id, attr_key_level=1):
        return Attribute.query.filter(Attribute.sensor_id == sensor_id, Attribute.is_key_attribute == attr_key_level)

    @staticmethod
    def get_all_urls(sensor_id):
        return Url.query.filter_by(sensor_id=sensor_id).all()

    @staticmethod
    def get_all_details(page=1, per_page=50):
        query = (db.session
                 .query(
                    Sensor.sensor_id,
                    Sensor.name,
                    Sensor.category,
                    Sensor.frequency,
                    MachineSensorMap.machine_id,
                    MachineSensorMap.machine_name)
                 .outerjoin(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id))
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        key_sensors = paginated.items
        total = paginated.total

        sensor_details = []
        for sensor in key_sensors:

            key_attributes = db.session.query(Attribute).filter(Attribute.sensor_id == sensor.sensor_id).all()

            attributes = [
                {'id': attr.attribute_id, 'name': attr.attribute, 'level': attr.is_key_attribute} for
                attr in key_attributes]

            # Fetch URL for each sensor
            urls = db.session.query(Url).filter(Url.sensor_id == sensor.sensor_id).all()
            url_dict = {url.url_type: url.url for url in urls}

            sensor_details.append({
                'id': sensor.sensor_id,
                'name': sensor.name,
                'category': sensor.category,
                'frequency': sensor.frequency,
                'machine_id': sensor.machine_id,
                'machine_name': sensor.machine_name,
                'attributes': attributes,  # Your existing code for attributes
                'urls': url_dict
            })
        return sensor_details, total


def next_short_id():
    """
    Generate a short unique device ID.

    This utility function combines the current time and a portion of a UUID to produce a unique string.

    :return: A unique string to be used as a device_id.
    """
    current_time_str = str(int(time.time()))
    uid = uuid.uuid4().bytes_le[:4].hex()
    return current_time_str + uid
