from flask import Flask
from waitress import serve
from flask import render_template
from flask import request,url_for,send_file,send_from_directory,redirect,flash,Markup,Response,session
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pymysql
from werkzeug.utils import secure_filename
import os
import logging
import sys
import json
import numpy as np
from flask_mail import Mail
from flask_mail import Message
from flask_uploads import *
from PIL import Image, ImageDraw, ImageFont
from forms import criarUsuario as novoUsuario
from flask_bootstrap import Bootstrap
import hashlib
from flask_migrate import Migrate

app = Flask(__name__)
bootstrap = Bootstrap(app)

from models import database
db = database.db
migrate = Migrate()
migrate.init_app(app,db)

WORKING_DIR='/flask/'
FONT_PATH = "/fonts/Times_New_Roman_Bold.ttf"

#HttpAuth
auth = HTTPBasicAuth()
#E-MAIL
mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ''

#LOG
logging.basicConfig(filename=WORKING_DIR + 'app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)

#SENHAS
lines = [line.rstrip('\n') for line in open(WORKING_DIR + 'senhas.pass')]
PASSWORD = lines[0]
GMAIL_PASSWORD = lines[1]
SESSION_SECRET_KEY = lines[2]
app.config['SECRET_KEY'] = SESSION_SECRET_KEY
app.config['MAIL_PASSWORD'] = GMAIL_PASSWORD
mail = Mail(app)

'''
https://flask-wtf.readthedocs.io/en/stable/index.html
https://wtforms.readthedocs.io/en/2.3.x/
'''

#BANCO DE DADOS
DB_USER = 'root'
DB_DATABASE = 'flask'
DB_PASSWORD = PASSWORD
DB_HOST = 'db_flask'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + '/' + DB_DATABASE + '?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'eTxYXyu5Hf6KGT'
db.init_app(app)

#Carregando tabela de usuários
from models import user as Usuarios

#TEMA
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'cerulean'

@app.before_first_request
def inicializar_bd():
    #db.drop_all()
    db.create_all()
    if (len(Usuarios.Users.query.all())==0):
        roleAdmin = Usuarios.Roles(name='admin',description='Administrador do Sistema')
        admin = Usuarios.Users(email='rafael.mota@ufca.edu.br', password=hashlib.sha1(b'autoridade').hexdigest(),username='admin')
        db.session.add(roleAdmin)
        db.session.add(admin)
        db.session.commit()
        id_usuario = Usuarios.Users.query.first().id
        id_role = Usuarios.Roles.query.first().id
        user_role = Usuarios.Roles_users(user_id=id_usuario,role_id=id_role)
        db.session.add(user_role)
        db.session.commit()

'''
Iniciar:
Executar em um python iterativo do container
from root import app
from root import db
app.app_context().push()
db.create_all()
'''

@auth.verify_password
def verify_password(username, password):
    senha = hashlib.sha1(password.encode('utf-8')).hexdigest()
    linha = Usuarios.Users.query.filter_by(username=username,password=senha).all()
    if (len(linha)>0):
        return (username)
    else:
        return(False)

@auth.get_user_roles
def get_user_roles(user):
    linhas = Usuarios.Users.query.filter_by(username=auth.username()).all()
    try:
        id_usuario = linhas[0].id
    except:
        logging.error("Erro ao pegar id do usuário")
        logging.error(auth.username())
        return ([])
    linhas = Usuarios.Roles_users.query.filter_by(user_id=id_usuario).all()
    roles = []
    for linha in linhas:
        role_id = linha.role_id
        role_name = Usuarios.Roles.query.filter_by(id=role_id).first().name
        roles.append(role_name)
    session['roles'] = roles
    return (roles)

@app.route('/')
def root():
    return (render_template('index.html',titulo='Sistema XXX'))

@app.route('/criarUsuario',methods=['POST','GET'])
@auth.login_required(role='admin')
def criarUsuario():
    if request.method == "POST":
        pass
        form = novoUsuario.NewUserForm()
        if form.validate_on_submit(): #TUDO OK COM O FORM ?
            if request.form['inserir']=='1': #INSERT
                usuario = Usuarios.Users(email=str(request.form['email']), password=hashlib.sha1(str(request.form['password']).encode('utf-8')).hexdigest(),username=str(request.form['username']))
                db.session.add(usuario)
                db.session.commit()
            else: #UPDATE
                pass
            return(redirect(url_for('/')))
        else: #Se o formulário não estiver preenchido corretamente
            return(render_template('form.html',form=form,action='/criarUsuario',titulo=u"Adicionar novo Usuário"))
    else:     #Se o método for o get
        if ('update' in request.args): #ATUALIZAR USUARIO
            atualizar = str(request.args.get('update'))
            if (atualizar=='1'):
                pass
        elif ('listar' in request.args): #LISTAR USUÁRIOS
            listar = str(request.args.get('listar'))
            if (listar=='1'):
                Usuarios.Users.query.all()
                return (render_template('tabela.html'))

        else: #CADASTRAR NOVO USUÁRIO
            form = novoUsuario.NewUserForm(inserir='1')
            return (render_template('form.html',form=form,action='/criarUsuario',titulo=u"Adicionar novo Usuário"))

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=80, url_prefix='/web')
