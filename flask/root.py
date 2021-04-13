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

app = Flask(__name__)

WORKING_DIR='/flask/'
FONT_PATH = "/fonts/Times_New_Roman_Bold.ttf"

auth = HTTPBasicAuth()
mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ''

logging.basicConfig(filename=WORKING_DIR + 'app.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s',level=logging.ERROR)

#Obtendo senhas
lines = [line.rstrip('\n') for line in open(WORKING_DIR + 'senhas.pass')]
PASSWORD = lines[0]
GMAIL_PASSWORD = lines[1]
SESSION_SECRET_KEY = lines[2]
app.config['SECRET_KEY'] = SESSION_SECRET_KEY
app.config['MAIL_PASSWORD'] = GMAIL_PASSWORD
mail = Mail(app)

@app.route('/')
def root():
    return ('Hello, World!')

if __name__ == "__main__":
    #app.run()
    serve(app, host='0.0.0.0', port=80, url_prefix='/web')
