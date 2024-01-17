from api import db
from sqlalchemy import cast, Boolean
from api.models.machine import Machine, MachineSensorMap, MachineOverview, MachineResult
from api.models.sensor import Sensor, Attribute, Url


class MachineDAO:

    @staticmethod
    def add(name, type, vender, year, lab_id):
        new_machine = Machine()
        db.session.add(new_machine)
        db.session.commit()
        return new_machine

    @staticmethod
    def read_machine(machine_id):
        current_machine = Machine.query.get(machine_id)
        if current_machine:
            return current_machine
        else:
            return None

    @staticmethod
    def delete_machine(machine_identifier):
        machine_to_delete = Machine.query.get(machine_identifier)
        if machine_to_delete:
            db.session.delete(machine_to_delete)
            db.session.commit()
            return machine_to_delete
        return None

    @staticmethod
    def update_machine(machine_identifier, update_data):
        machine_to_update = Machine.query.get(machine_identifier)
        if machine_to_update:
            for key, value in update_data.items():
                setattr(machine_to_update, key, value)
            db.session.commit()
            return machine_to_update
        return None

    @staticmethod
    def get_single(machine_identifier):

        if isinstance(machine_identifier, int):
            machine = Machine.query.get(machine_identifier)
        elif isinstance(machine_identifier, str):
            machine = Machine.query.filter_by(name=machine_identifier).first()
        else:
            raise ValueError('machine_identifier must be either an id or a name')
        return machine

    @staticmethod
    def get_single_overview(machine_identifier):
        if isinstance(machine_identifier, int):
            machine_overview = MachineOverview.query.get(machine_identifier)
        elif isinstance(machine_identifier, str):
            machine_overview = MachineOverview.query.filter_by(name=machine_identifier).first()
        else:
            raise ValueError('machine_identifier must be either an id or a name')
        return machine_overview

    @staticmethod
    def update_machine_overview(machine_identifier, update_data):
        if isinstance(machine_identifier, int):
            machine_overview_to_update = MachineOverview.query.get(machine_identifier)
        elif isinstance(machine_identifier, str):
            machine_overview_to_update = MachineOverview.query.filter_by(name=machine_identifier).first()
        else:
            raise ValueError('machine_identifier must be either an id or a name')

        if machine_overview_to_update:
            # Update attributes
            for key, value in update_data.items():
                if hasattr(machine_overview_to_update, key):
                    setattr(machine_overview_to_update, key, value)
            # Commit changes to the database
            db.session.commit()
            return machine_overview_to_update
        return None

    @staticmethod
    def get_single_result(machine_identifier):
        if isinstance(machine_identifier, int):
            machine_result = MachineResult.query.get(machine_identifier)
        elif isinstance(machine_identifier, str):
            machine_result = MachineResult.query.filter_by(name=machine_identifier).first()
        else:
            raise ValueError('machine_identifier must be either an id or a name')
        return machine_result

    @staticmethod
    def update_machine_result(machine_identifier, update_data):
        if isinstance(machine_identifier, int):
            machine_result_to_update = MachineResult.query.get(machine_identifier)
        elif isinstance(machine_identifier, str):
            machine_result_to_update = MachineResult.query.filter_by(name=machine_identifier).first()
        else:
            raise ValueError('machine_identifier must be either an id or a name')

        if machine_result_to_update:
            for key, value in update_data.items():
                if hasattr(machine_result_to_update, key):
                    setattr(machine_result_to_update, key, value)
            # Commit changes to the database
            db.session.commit()
            return machine_result_to_update
        return None

    @staticmethod
    def get_all(page=1, per_page=30):
        paginated = Machine.query.paginate(page=page, per_page=per_page, error_out=False)
        return paginated.items, paginated.pages, paginated.total

    @staticmethod
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

    @staticmethod
    def get_sensors(machine_identifier, page=1, per_page=10):
        if isinstance(machine_identifier, int):

            query = (db.session
                     .query(Sensor)
                     .join(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id)
                     .filter(MachineSensorMap.machine_id == machine_identifier))
        elif isinstance(machine_identifier, str):
            query = (db.session
                     .query(Sensor)
                     .join(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id)
                     .filter(MachineSensorMap.machine_name == machine_identifier))
        else:
            raise ValueError('machine_identifier must be either an id or a name')

        if per_page is not None:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            return paginated.items, paginated.total
        else:
            sensors = query.all()
            return sensors, len(sensors)

    @staticmethod
    def get_key_sensors(machine_identifier, page=1, per_page=10):
        if isinstance(machine_identifier, int):
            query = (db.session
                     .query(Sensor)
                     .join(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id)
                     .filter(MachineSensorMap.machine_id == machine_identifier, MachineSensorMap.is_key_sensor == 1))
        elif isinstance(machine_identifier, str):
            query = (db.session
                     .query(Sensor)
                     .join(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id)
                     .filter(MachineSensorMap.machine_name == machine_identifier, MachineSensorMap.is_key_sensor == 1))
        else:
            raise ValueError('machine_identifier must be either an id or a name')

        if per_page is not None:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            key_sensors = paginated.items
            total = paginated.total
        else:
            key_sensors = query.all()
            print(key_sensors)
            return key_sensors, len(key_sensors)

        sensor_details = []

        for sensor in key_sensors:
            key_attributes = db.session.query(Attribute).filter(Attribute.sensor_id == sensor.sensor_id,
                                                                Attribute.is_key_attribute == 1).all()

            attributes = [
                {'attribute_id': attr.attribute_id, 'name': attr.attribute, 'level': attr.is_key_attribute} for
                attr in key_attributes]

            # Fetch URL for each sensor
            urls = db.session.query(Url).filter(Url.sensor_id == sensor.sensor_id).all()
            url_dict = {url.url_type: url.url for url in urls}

            sensor_details.append({
                'id': sensor.sensor_id,
                'name': sensor.name,
                'category': sensor.category,
                'attributes': attributes,  # Your existing code for attributes
                'urls': url_dict
            })

        return sensor_details, total

    @staticmethod
    def get_key_info(machine_identifier, sensor_key_level=1, attr_key_level=1):
        if isinstance(machine_identifier, int):

            sensors = (db.session.query(Sensor)
                       .join(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id)
                       .filter(MachineSensorMap.machine_id == machine_identifier, MachineSensorMap.is_key_sensor == sensor_key_level)
                       .all())
        elif isinstance(machine_identifier, str):
            sensors = (db.session.query(Sensor)
                       .join(MachineSensorMap, Sensor.sensor_id == MachineSensorMap.sensor_id)
                       .filter(MachineSensorMap.machine_name == machine_identifier, MachineSensorMap.is_key_sensor == sensor_key_level)
                       .all())
        else:
            raise ValueError('machine_identifier must be either an id or a name')
        sensor_details = []
        for sensor in sensors:
            # Fetch key attributes for each sensor
            key_attributes = db.session.query(Attribute).filter(Attribute.sensor_id == sensor.sensor_id,
                                                                Attribute.is_key_attribute == attr_key_level).all()
            attributes = [
                {'id': attr.attribute_id, 'name': attr.attribute, 'level': attr.is_key_attribute} for
                attr in key_attributes]

            # Fetch URL for each sensor
            urls = db.session.query(Url).filter(Url.sensor_id == sensor.sensor_id).all()
            url_dict = {url.url_type: url.url for url in urls}
            # url_list = [{'url_id': url.url_id, 'url': url.url, 'url_type': url.url_type} for url in urls]

            sensor_details.append({
                'id': sensor.sensor_id,
                'attributes': attributes,
                'urls': url_dict
            })

        return sensor_details

