from flask_sqlalchemy import SQLAlchemy

# Base repository providing common CRUD operations

class BaseRepository:
    def __init__(self, db: SQLAlchemy, model):
        self.db = db
        self.model = model

    def get(self, id):
        return self.model.query.get(id)

    def all(self):
        return self.model.query.all()

    def add(self, instance):
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def delete(self, instance):
        self.db.session.delete(instance)
        self.db.session.commit()

    def filter_by(self, **kwargs):
        return self.model.query.filter_by(**kwargs)
