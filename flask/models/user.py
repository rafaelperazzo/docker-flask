from models import database

class User(database.db.Model):
    id = database.db.Column(database.db.Integer, primary_key=True)
    username = database.db.Column(database.db.String(80), unique=True, nullable=False)
    password = database.db.Column(database.db.String(80), unique=False, nullable=False)
    email = database.db.Column(database.db.String(120), unique=True, nullable=False)
    roles = database.db.Column(database.db.String(100), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username