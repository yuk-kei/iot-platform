from ..dao.machine_dao import MachineDAO
from ..dao.sensor_dao import SensorDAO,

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
        dao = MachineDAO(connection_pool=None)
        return dao.get_key_sensors(machine_id, page, per_page)

    @staticmethod
    def get_key_info(machine_id):
        dao = MachineDAO(connection_pool=None)
        return dao.get_key_info(machine_id)

    @staticmethod
    def get_key_sensor_details(machine_id):

        key_sensors = MachineDAO.get_key_sensors(machine_id)  # Adjust based on actual method name and parameters
        sensor_details = []

        for sensor in key_sensors:
            key_attributes = SensorDao.get_key_attributes(sensor.sensor_id)
            attributes = [
                {'attribute_id': attr.attribute_id, 'key_name': attr.attribute, 'key_value': attr.is_key_attribute} for
                attr in key_attributes]



            sensor_details.append({
                'sensor_id': sensor.sensor_id,
                'attributes': attributes,
                'urls': url_list
            })

        return sensor_details