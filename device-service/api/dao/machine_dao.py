from ..models.machine import Machine
from .. import db


class MachineDAO:
   @staticmethod
   def create_machine(machine_uuid,name, type, vendor, year, lab_id):
      new_machine = Machine(machine_uuid=machine_uuid,name=name, type=type, vendor=vendor,
                          year=year, lab_id=lab_id)
      db.session.add(new_machine)
      db.session.commit()
      return new_machine

   def read_machine(machine_id):
      current_machine = Machine.query.get(machine_id)
      if current_machine:
         return current_machine
      else:
         return None

   @staticmethod
   def delete_machine(machine_id):
      machine_to_delete = Machine.query.get(machine_id)
      if machine_to_delete:
         db.session.delete(machine_to_delete)
         db.session.commit()
         return machine_to_delete
      return None

   @staticmethod
   def update_machine(machine_id, update_data):
      machine_to_update = Machine.query.get(machine_id)
      if machine_to_update:
         for key, value in update_data.items():
            setattr(machine_to_update, key, value)
         db.session.commit()
         return machine_to_update
      return None
