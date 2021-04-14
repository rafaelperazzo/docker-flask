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
from forms import app_forms

app = Flask(__name__)

from models import database
db = database.db

WORKING_DIR='/flask/'
FONT_PATH = "/fonts/Times_New_Roman_Bold.ttf"

#E-MAIL
auth = HTTPBasicAuth()
mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ''

#LOG
logging.basicConfig(filename=WORKING_DIR + 'app.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s',level=logging.ERROR)

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
db.init_app(app)

#Carregando tabela de usuários
from models import user as Usuarios

'''
Iniciar:
Executar em um python iterativo do container
from root import app
from root import db
app.app_context().push()
db.create_all()
'''

@app.route('/')
def root():
    #form = app_forms.MyForm()
    return (render_template('index.html',form=form))

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=80, url_prefix='/web')
