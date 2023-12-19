from ..dao.machine_dao import MachineDAO
from ..dao.sensor_dao import SensorDAO

from flask import current_app


class MachineService:
    @staticmethod
    def get_all(page=1, per_page=10, use_raw_sql=False):
        # dao = MachineDAO(current_app.config['MYSQL_POOL'])
        dao = MachineDAO(connection_pool=None)
        MachineDAO(connection_pool=None)
        if not use_raw_sql:
            return dao.get_all(page, per_page)
        else:
            return dao.get_all_sql(page, per_page)

    @staticmethod
    def get_sensors(machine_id, page=1, per_page=10, use_raw_sql=False):
        dao = MachineDAO(connection_pool=None)

        return dao.get_sensors(machine_id, page, per_page)

    @staticmethod
    def get_key_sensors(machine_id, page=1, per_page=10, use_raw_sql=False):
        machine_dao = MachineDAO(connection_pool=None)
        sensor_dao = SensorDAO(connection_pool=None)

        key_sensors, total = machine_dao.get_key_sensors(machine_id=machine_id, page=page, per_page=per_page)
        sensor_details = []

        for sensor in key_sensors:
            key_attributes = sensor_dao.get_key_attribute(sensor.sensor_id)
            attributes = [attr.attribute for attr in key_attributes]
            urls = sensor_dao.get_all_urls(sensor.sensor_id)

            url_dict = {url.url_type: url.url for url in urls}

            sensor_details.append({
                'sensor_id': sensor.sensor_id,
                'sensor_name': sensor.name,
                'category': sensor.category,
                'attributes': attributes,  # Your existing code for attributes
                'urls': url_dict
            })

        return sensor_details, total

    @staticmethod
    def get_key_info(machine_id):
        dao = MachineDAO(connection_pool=None)
        return dao.get_key_info(machine_id)

    @staticmethod
    def get_key_sensor_details(machine_id):
        machine_dao = MachineDAO(connection_pool=None)
        sensor_dao = SensorDAO(connection_pool=None)

        key_sensors = machine_dao.get_key_sensors(machine_id)  # Adjust based on actual method name and parameters

        sensor_details = []

        for sensor in key_sensors[0]:
            key_attributes = sensor_dao.get_key_attribute(sensor.sensor_id)
            attributes = [attr.attribute for attr in key_attributes]
            urls = sensor_dao.get_all_urls(sensor.sensor_id)

            url_dict = {url.url_type: url.url for url in urls}

            sensor_details.append({
                'sensor_id': sensor.sensor_id,
                'attributes': attributes,  # Your existing code for attributes
                'urls': url_dict
            })

        return sensor_details
