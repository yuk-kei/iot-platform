from ..models.lab import Lab
from ..models.machine import Machine, MachineSensorMap
from .machine_dao import MachineDAO
from ..models.sensor import Sensor
from .. import db


class LabDAO:

    @staticmethod
    def get_single(lab_identifier):
        if isinstance(lab_identifier, int):
            return Lab.query.get(lab_identifier)
        elif isinstance(lab_identifier, str):
            return Lab.query.filter_by(name=lab_identifier).first()
        else:
            raise ValueError('lab_identifier must be either an id or a name')

    @staticmethod
    def get_all(page=None, per_page=30):
        if page is None:
            return Lab.query.all()
        else:
            paginated = Lab.query.paginate(page=page, per_page=per_page, error_out=False)
            return paginated.items, paginated.total

    @staticmethod
    def get_key_info_from_lab(lab_identifier):
        if isinstance(lab_identifier, int):
            machine_info = (db.session.query(Machine.machine_id, Machine.name)
                            .filter(Machine.lab_id == lab_identifier)
                            .all())
            # machine_names = [m[0] for m in machine_info]

        elif isinstance(lab_identifier, str):
            machine_info = (db.session.query(Machine.name)
                            .filter(Machine.lab_name == lab_identifier)
                            .all())
            # machine_ids = [m[0] for m in machine_info]

        else:
            raise ValueError('lab_identifier must be either an id or a name')

        results = []
        for machine_id, machine_name in machine_info:
            sensor_details = MachineDAO.get_key_info(machine_id, sensor_key_level=2, attr_key_level=2)
            machine_details = {machine_name: sensor_details}
            results.append(machine_details)
        return results
