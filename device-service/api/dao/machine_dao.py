from ..models.machine import Machine
from .. import db
from sqlalchemy import cast, Boolean
from ..models.machine import Machine, MachineSensorMap
from ..models.sensor import Sensor, Attribute, Url


class MachineDAO:

    def __init__(self, connection_pool=None):
        self.connection_pool = connection_pool

    def add(self, name, type, vender, year, lab_id):
        new_machine = Machine()
        db.session.add(new_machine)
        db.session.commit()
        return new_machine

    def read_machine(self, machine_id):
        current_machine = Machine.query.get(machine_id)
        if current_machine:
            return current_machine
        else:
            return None

    def delete_machine(self, machine_id):
        machine_to_delete = Machine.query.get(machine_id)
        if machine_to_delete:
            db.session.delete(machine_to_delete)
            db.session.commit()
            return machine_to_delete
        return None

    def update_machine(self, machine_id, update_data):
        machine_to_update = Machine.query.get(machine_id)
        if machine_to_update:
            for key, value in update_data.items():
                setattr(machine_to_update, key, value)
            db.session.commit()
            return machine_to_update
        return None

    def get_all(self, page=1, per_page=30):
        paginated = Machine.query.paginate(page=page, per_page=per_page, error_out=False)
        return paginated.items, paginated.pages, paginated.total

    def get_all_sql(self, page, per_page):
        sql = "SELECT * FROM machine"
        if page and per_page:
            sql += " LIMIT %s OFFSET %s"
            offset = (page - 1) * per_page
            params = (per_page, offset)
        else:
            params = None
        with self.connection_pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchall()
                return result

    def get_sensors(self, machine_id, page=1, per_page=10):
        query = (db.session
                 .query(Sensor)
                 .join(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id)
                 .filter(MachineSensorMap.machine_id == machine_id))

        if per_page is not None:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            return paginated.items, paginated.total
        else:
            sensors = query.all()
            return sensors, len(sensors)

    def get_key_sensors(self, machine_id, page=1, per_page=10):
        query = (db.session
                 .query(Sensor)
                 .join(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id)
                 .filter(MachineSensorMap.machine_id == machine_id, MachineSensorMap.is_key_sensor == True))

        if per_page is not None:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            return paginated.items, paginated.total
        else:
            key_sensors = query.all()
            return key_sensors, len(key_sensors)

    @staticmethod
    def get_key_info(machine_id):
        sensors = (db.session.query(Sensor)
                   .join(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id)
                   .filter(MachineSensorMap.machine_id == machine_id, MachineSensorMap.is_key_sensor == True)
                   .all())

        sensor_details = []
        for sensor in sensors:
            # Fetch key attributes for each sensor
            key_attributes = db.session.query(Attribute).filter(Attribute.sensor_id == sensor.sensor_id, Attribute.is_key_attribute == True).all()
            attributes = [{'attribute_id': attr.attribute_id, 'key_name': attr.attribute, 'key_value': attr.is_key_attribute} for attr in key_attributes]

            # Fetch URL for each sensor
            urls = db.session.query(Url).filter(Url.sensor_id == sensor.sensor_id).all()
            url_list = [{'url_id': url.url_id, 'url': url.url, 'url_type': url.url_type} for url in urls]

            sensor_details.append({
                'sensor_id': sensor.sensor_id,
                'attributes': attributes,
                'urls': url_list
            })

        return sensor_details

