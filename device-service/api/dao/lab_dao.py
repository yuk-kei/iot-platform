from ..models.lab import Lab
from .. import db


class LabDAO:
    def __init__(self):
        pass
    @staticmethod
    def create_lab(name, type):
        new_lab = Lab(name=name, type=type)
        db.session.add(new_lab)
        db.session.commit()
        return new_lab

    def read_lab(lab_id):
        current_lab = Lab.query.get(lab_id)
        if current_lab:
            return current_lab
        else:
            return None

    @staticmethod
    def delete_lab(lab_id):
        lab_to_delete = Lab.query.get(lab_id)
        if lab_to_delete:
            db.session.delete(lab_to_delete)
            db.session.commit()
            return lab_to_delete
        return None

    @staticmethod
    def update_lab(lab_id, update_data):
        lab_to_update = Lab.query.get(lab_id)
        if lab_to_update:
            for key, value in update_data.items():
                setattr(lab_to_update, key, value)
            db.session.commit()
            return lab_to_update
        return None


