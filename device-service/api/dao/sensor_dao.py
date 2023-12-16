from ..models.sensor import Sensor, Attribute, Url
from .. import db


class SensorDAO:
    def __init__(self, connection_pool=None):
        self.connection_pool = connection_pool

    def get_all(self, page=None, per_page=30):
        if page is None:
            return Sensor.query.all()
        else:
            paginated = Sensor.query.paginate(page=page, per_page=per_page, error_out=False)
            return paginated.items, paginated.pages, paginated.total

    def get_by_id(self, sensor_id):
        return Sensor.query.get(sensor_id)

    def get_all_attributes(self, sensor_id, page=None, per_page=30):
        if page is None:
            return Attribute.query.get(sensor_id).attributes
        else:
            paginated = (Attribute.query(sensor_id).paginate(page=page, per_page=per_page, error_out=False))
            return paginated.items, paginated.pages, paginated.total

    @staticmethod
    def get_key_attribute(sensor_id):
        return Attribute.query.get(sensor_id).filter(Attribute.is_key_attribute == True)

    def get_all_urls(self, sensor_id):
        return Url.query.get(sensor_id).urls
