from models import database
import datetime
import random
import string

def genToken(size=24, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
        return ''.join(random.choice(chars) for _ in range(size))

class Templates(database.db.Model):
    id = database.db.Column(database.db.Integer(), primary_key=True)
    tipo = database.db.Column(database.db.Integer(), unique=False)
    nome = database.db.Column(database.db.String(50), unique=False)
    descricao = database.db.Column(database.db.String(300), unique=False)
    arquivo = database.db.Column(database.db.String(200), unique=False)
    x = database.db.Column(database.db.String(100), unique=False)
    y = database.db.Column(database.db.String(100), unique=False)
    tamanhos = database.db.Column(database.db.String(100), unique=False)
    alinhamentos = database.db.Column(database.db.String(100), unique=False)
    create_date = database.db.Column(database.db.DateTime,unique=False,nullable=True,default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    quantidade_textos = database.db.Column(database.db.Integer(), unique=False)

class Documentos(database.db.Model):
    id = database.db.Column(database.db.Integer(), primary_key=True)
    id_template = database.db.Column(database.db.Integer,database.db.ForeignKey('templates.id'),nullable=False)
    template = database.db.relationship('Templates',foreign_keys='Documentos.id_template')
    nome = database.db.Column(database.db.String(100), unique=False)
    textos = database.db.Column(database.db.Text, unique=False)
    token = database.db.Column(database.db.String(25), unique=True,nullable=True,default=genToken())
    create_date = database.db.Column(database.db.DateTime,unique=False,nullable=True,default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))