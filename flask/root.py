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
from flask_wtf.csrf import CsrfProtect
import configparser

app = Flask(__name__)
bootstrap = Bootstrap(app)
CsrfProtect(app)
config = configparser.ConfigParser()
config.read('/flask/config.ini')

from models import database
db = database.db
migrate = Migrate()
migrate.init_app(app,db)

WORKING_DIR= config['DEFAULT']['working_dir']
FONT_PATH = config['DEFAULT']['font_path']

#HttpAuth
auth = HTTPBasicAuth()

#E-MAIL
mail = Mail(app)
app.config['MAIL_SERVER'] = config['EMAIL']['mail_server']
app.config['MAIL_PORT'] = config['EMAIL']['mail_port']
app.config['MAIL_USERNAME'] = config['EMAIL']['mail_username']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ''
app.config['SECRET_KEY'] = config['DEFAULT']['secret_key']
app.config['MAIL_PASSWORD'] = config['EMAIL']['mail_password']
mail = Mail(app)

#LOG
logging.basicConfig(filename=WORKING_DIR + config['DEFAULT']['log_file'], filemode=config['DEFAULT']['log_write'], format='%(asctime)s %(name)s - %(levelname)s - %(message)s',level=int(config['DEFAULT']['log_type']))

'''
https://flask-wtf.readthedocs.io/en/stable/index.html
https://wtforms.readthedocs.io/en/2.3.x/
'''

#BANCO DE DADOS
DB_USER = config['DB']['db_user']
DB_DATABASE = config['DB']['db_database']
DB_PASSWORD = config['DB']['db_password']
DB_HOST = config['DB']['db_host']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + '/' + DB_DATABASE + '?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'eTxYXyu5Hf6KGT'
db.init_app(app)

#Carregando tabela de usuários
from models import user as Usuarios

#TEMA
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = config['DEFAULT']['theme']

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

@app.route('/usuario/adicionar',methods=['POST','GET'])
@auth.login_required(role='admin')
def usuario_adicionar():
    if request.method == "POST":
        form = novoUsuario.NewUserForm()
        if form.validate_on_submit(): #TUDO OK COM O FORM ? ADICIONAR AO BD
            usuario = Usuarios.Users(email=str(request.form['email']), password=hashlib.sha1(str(request.form['password']).encode('utf-8')).hexdigest(),username=str(request.form['username']))
            db.session.add(usuario)
            db.session.commit()
            return(redirect(url_for('/')))
        else: #Se o formulário não estiver preenchido corretamente
            return(render_template('form.html',form=form,action='/usuario/adicionar',titulo=u"Adicionar novo Usuário"))
    else:     #Se o método for o get, abrir o formulário
        form = novoUsuario.NewUserForm(inserir='1')
        return (render_template('form.html',form=form,action='/usuario/adicionar',titulo=u"Adicionar novo Usuário"))

@app.route('/usuario/mostrarTodos',methods=['GET'])
@auth.login_required(role='admin')
def usuario_mostrarTodos():
    data = Usuarios.Users.query.order_by(Usuarios.Users.username).all()
    return(render_template('tabela.html',data=data))

@app.route('/usuario/<id>/editar',methods=['GET','POST'])
@auth.login_required(role='admin')
def usuario_editar(id):
    form = novoUsuario.NewUserForm()
    if request.method == "POST": #gravando alterações
        if form.validate_on_submit():
            usuario = Usuarios.Users.query.get(int(id))
            usuario.username = request.form['username']
            usuario.email = request.form['email']
            usuario.password = request.form['password']
            return(str(usuario.username))
        else:
            return(render_template('form.html',form=form,action='/usuario/' + str(id) + '/editar',titulo=u"Editando Usuário"))            
    else: #abrindo página de edição
        data = Usuarios.Users.query.filter_by(id=int(id)).first()
        form.username.data = data.username
        form.email.data = data.email
        form.password.data = data.password
        return(render_template('form.html',form=form,action='/usuario/' + str(id) + '/editar',titulo=u"Editando Usuário"))

@app.route('/usuario/<id>/excluir',methods=['GET','POST'])
@auth.login_required(role='admin')
def usuario_excluir(id):
    Usuarios.Users.query.filter(Usuarios.Users.id==int(id)).delete()
    #db.session.commit()
    return(redirect(url_for('usuario_mostrarTodos')))

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=80, url_prefix='/web')
