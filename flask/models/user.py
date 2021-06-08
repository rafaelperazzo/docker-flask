from models import database
import datetime

class Roles(database.db.Model):
    id = database.db.Column(database.db.Integer(), primary_key=True)
    name = database.db.Column(database.db.String(80), unique=True)
    description = database.db.Column(database.db.String(255))
    def __repr__(self):
        return '<Role %r>' % self.name

class Users(database.db.Model):
    id = database.db.Column(database.db.Integer, primary_key=True)
    name = database.db.Column(database.db.String(200), unique=False, nullable=False)
    username = database.db.Column(database.db.String(80), unique=True, nullable=False)
    password = database.db.Column(database.db.String(80), unique=False, nullable=False)
    email = database.db.Column(database.db.String(120), unique=True, nullable=False)
    create_date = database.db.Column(database.db.DateTime,unique=False,nullable=True,default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    def __repr__(self):
        return '<User %r>' % self.username

class Roles_users(database.db.Model):
    id = database.db.Column(database.db.Integer, primary_key=True)
    user_id = database.db.Column(database.db.Integer,database.db.ForeignKey('users.id'),nullable=False)
    user = database.db.relationship('Users',backref=database.db.backref('roles_users',lazy=True))
    role_id = database.db.Column(database.db.Integer,database.db.ForeignKey('roles.id'),nullable=False)
    role = database.db.relationship('Roles',backref=database.db.backref('roles_users',lazy=True))