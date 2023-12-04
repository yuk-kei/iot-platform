from ..models.sensor import Sensor
from .. import db


class SensorDAO:
   @staticmethod
   def create_sensor(sensor_uuid, name, category, sensor_type, sensor_vendor, vendor_pid, chip, rpi_id):
      new_sensor = Sensor(sensor_uuid = sensor_uuid, name=name, category=category, sensor_type=sensor_type, sensor_vendor=sensor_vendor,
                          vendor_pid=vendor_pid, chip=chip, rpi_id=rpi_id)
      db.session.add(new_sensor)
      db.session.commit()
      return new_sensor

   def read_sensor(sensor_id):
      current_sensor = Sensor.query.get(sensor_id)
      if current_sensor:
         return current_sensor
      else:
         return None

   @staticmethod
   def delete_sensor(sensor_id):
      sensor_to_delete = Sensor.query.get(sensor_id)
      if sensor_to_delete:
         db.session.delete(sensor_to_delete)
         db.session.commit()
         return sensor_to_delete
      return None

   @staticmethod
   def update_sensor(sensor_id, update_data):
      sensor_to_update = Sensor.query.get(sensor_id)
      if sensor_to_update:
         for key, value in update_data.items():
            setattr(sensor_to_update, key, value)
         db.session.commit()
         return sensor_to_update
      return None
