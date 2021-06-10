from string import Template
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
from forms import criarTemplate as FormTemplate
from forms import criarDocumento as FormDocumento
from flask_bootstrap import Bootstrap
import hashlib
from flask_migrate import Migrate
from flask_wtf.csrf import CsrfProtect
import configparser
from textwrapper import TextWrapper

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
DOCS_PATH = config['DEFAULT']['docs_path']
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
from models import documentos as Documentos

#TEMA
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = config['DEFAULT']['theme']

#TESTING
TESTING = 0
app.config['TESTING'] = 0
if int(config['DEFAULT']['testing'])==0:
    app.config['TESTING'] = 0
else:
    app.config['TESTING'] = 1

app.config['UPLOADED_IMAGES_DEST'] = WORKING_DIR + 'upload'
app.config['UPLOADS_DEFAULT_DEST'] = WORKING_DIR + 'upload'
modelos = UploadSet('modelos',IMAGES)
configure_uploads(app,modelos)
patch_request_class(app)


@app.before_first_request
def inicializar_bd():
    #db.drop_all()
    db.create_all()
    if (len(Usuarios.Users.query.all())==0):
        roleAdmin = Usuarios.Roles(name='admin',description='Administrador do Sistema')
        admin = Usuarios.Users(name='Rafael Perazzo',email='rafael.mota@ufca.edu.br', password=hashlib.sha1(b'autoridade').hexdigest(),username='admin')
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

@app.route('/testing/<id>',methods=['GET'])
@auth.login_required(role='admin')
def testing(id):
    modo = str(id)
    if (modo=='0'):
        app.config['TESTING'] = '0'
    else:
        app.config['TESTING'] = '1'
    return(redirect(url_for('root')))

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
@auth.login_required(role='admin')
def root():
    return (render_template('index.html',titulo='Sistema XXX',testing=app.config['TESTING'],roles=session['roles']))

@app.route('/usuario/adicionar',methods=['POST','GET'])
@auth.login_required(role='admin')
def usuario_adicionar():
    if request.method == "POST":
        form = novoUsuario.NewUserForm()
        if form.validate_on_submit(): #TUDO OK COM O FORM ? ADICIONAR AO BD
            usuario = Usuarios.Users(name=request.form['name'],email=str(request.form['email']), password=hashlib.sha1(str(request.form['password']).encode('utf-8')).hexdigest(),username=str(request.form['username']))
            db.session.add(usuario)
            db.session.commit()
            return(redirect(url_for('root')))
        else: #Se o formulário não estiver preenchido corretamente
            return(render_template('form.html',form=form,action='/usuario/adicionar',titulo=u"Adicionar novo Usuário",testing=app.config['TESTING']))
    else:     #Se o método for o get, abrir o formulário
        form = novoUsuario.NewUserForm(inserir='1')
        return (render_template('form.html',form=form,action='/usuario/adicionar',titulo=u"Adicionar novo Usuário",testing=app.config['TESTING']))

@app.route('/usuario/mostrarTodos',methods=['GET'])
@auth.login_required(role='admin')
def usuario_mostrarTodos():
    data = Usuarios.Users.query.order_by(Usuarios.Users.username).all()
    return(render_template('tabela.html',data=data,testing=app.config['TESTING']))

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
            usuario.name = request.form['name']
            #db.session.commit()
            return(redirect(url_for('usuario_mostrarTodos')))
        else:
            return(render_template('form.html',form=form,action='/usuario/' + str(id) + '/editar',titulo=u"Editando Usuário",testing=app.config['TESTING']))            
    else: #abrindo página de edição
        data = Usuarios.Users.query.filter_by(id=int(id)).first()
        form.username.data = data.username
        form.email.data = data.email
        form.password.data = data.password
        form.name.data = data.name
        return(render_template('form.html',form=form,action='/usuario/' + str(id) + '/editar',titulo=u"Editando Usuário",testing=app.config['TESTING']))

@app.route('/usuario/<id>/excluir',methods=['GET','POST'])
@auth.login_required(role='admin')
def usuario_excluir(id):
    Usuarios.Users.query.filter(Usuarios.Users.id==int(id)).delete()
    db.session.commit()
    return(redirect(url_for('usuario_mostrarTodos')))

def gerarCertificado(textos,x,y,tamanhos, alinhamentos,template, font_path,output_png, output_pdf):
   
    img = Image.open(template, mode ='r')    
    draw = ImageDraw.Draw(img)
    image_width = img.width

    for i in range(0,len(textos),1):
        font = ImageFont.truetype(font_path,tamanhos[i])
        text_width, _ = draw.textsize(textos[i], font = font)
        if (alinhamentos[i]==0):
            draw.multiline_text((x[i],y[i]),textos[i],font = font,fill=(0,0,0))
        else:
            centro = (image_width - text_width) / 2
            draw.multiline_text((centro,y[i]),textos[i],font = font,fill=(0,0,0))

    # saves the image in png format
    img.save(output_png)
    image1 = Image.open(output_png)
    im1 = image1.convert('RGB')
    im1.save(output_pdf)

def getData(cidade):
    Meses=('janeiro','fevereiro',u'março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro')
    hoje = datetime.date.today()
    dia = hoje.day
    mes = hoje.month
    ano = hoje.year
    mes = Meses[mes]
    hoje = cidade + " " + str(dia) + " de " + mes + " de " + str(ano)
    return (hoje)

@app.route('/certificado',methods=['GET','POST'])
@auth.login_required(role='admin')
def certificado():
    
    template = DOCS_PATH + "declaracao1.png"
    output_png = DOCS_PATH + 'output.png'
    output_pdf = DOCS_PATH + 'output.pdf'
    font = ImageFont.truetype(FONT_PATH,20)
    nome = "RAFAEL PERAZZO BARBOSA MOTA - 1570709"
    motivo = "Motivo da ausencia"
    wrapper = TextWrapper(motivo, font, 1000)
    motivo = wrapper.wrapped_text()
    data = getData("Juazeiro do Norte")
    gestor = "RAFAEL PERAZZO BARBOSA MOTA"
    siape = "1570709"
    textos = [nome,motivo,data,gestor,siape]
    x = [300,130,900,450,600]
    y = [1050,1200,1550,1750,1790]
    tamanhos = [24,24,24,24,24]
    alinhamentos = [0,0,0,1,1]
    gerarCertificado(textos,x,y,tamanhos,alinhamentos,template,FONT_PATH,output_png,output_pdf)
    return (send_from_directory(DOCS_PATH, 'output.pdf'))

@app.route('/template/adicionar',methods=['POST','GET'])
@auth.login_required(role='admin')
def template_adicionar():
    if request.method == "POST":
        form = FormTemplate.NewTemplateForm()
        if form.validate_on_submit(): #TUDO OK COM O FORM ? ADICIONAR AO BD
            modelos.save(request.files['arquivo'])            
            template = Documentos.Templates(nome=request.form['nome'],arquivo=request.files['arquivo'].filename,x=request.form['x'],y=request.form['y'],tamanhos=request.form['tamanhos'],alinhamentos=request.form['alinhamentos'],quantidade_textos=request.form['quantidade_textos'],tipo=request.form['tipo'],descricao=request.form['descricao'])
            db.session.add(template)
            db.session.commit()
            return(redirect(url_for('template_listar')))
        else: #Se o formulário não estiver preenchido corretamente
            return(render_template('form.html',form=form,action='/template/adicionar',titulo=u"Adicionar novo Template",testing=app.config['TESTING']))
    else:     #Se o método for o get, abrir o formulário
        form = FormTemplate.NewTemplateForm()
        return (render_template('form.html',form=form,action='/template/adicionar',titulo=u"Adicionar novo Template",testing=app.config['TESTING']))

@app.route('/template/listar',methods=['GET'])
@auth.login_required(role='admin')
def template_listar():
    data = Documentos.Templates.query.order_by(Documentos.Templates.create_date).all()
    return(render_template('templates.html',data=data,testing=app.config['TESTING'],titulo='Lista de Templates'))

@app.route('/template/<id>/excluir',methods=['GET','POST'])
@auth.login_required(role='admin')
def template_excluir(id):
    Documentos.Templates.query.filter(Documentos.Templates.id==int(id)).delete()
    db.session.commit()
    return(redirect(url_for('template_listar')))

@app.route('/template/<id>/editar',methods=['GET','POST'])
@auth.login_required(role='admin')
def template_editar(id):
    form = FormTemplate.NewTemplateForm()
    
    if request.method == "POST": #gravando alterações
        
        if form.validate_on_submit():
            template = Documentos.Templates.query.get(int(id))
            template.tipo = request.form['tipo']
            template.descricao=request.form['descricao']
            template.nome = request.form['nome']
            template.arquivo = request.form['arquivo']
            template.x = request.form['x']
            template.y = request.form['y']
            template.tamanhos = request.form['tamanhos']
            template.alinhamentos = request.form['alinhamentos']
            template.quantidade_textos = request.form['quantidade_textos']
            db.session.commit()
            return(redirect(url_for('template_listar')))
        
        else:
            return(render_template('form.html',form=form,action='/template/' + str(id) + '/editar',titulo=u"Editando Template",testing=app.config['TESTING']))            
        
    else: #abrindo página de edição
        data = Documentos.Templates.query.filter_by(id=int(id)).first()
        form.tipo.data = data.tipo
        form.nome.data = data.nome
        form.descricao.data = data.descricao
        form.arquivo.data = data.arquivo
        form.quantidade_textos.data = data.quantidade_textos
        form.x.data = data.x
        form.y.data = data.y
        form.tamanhos.data = data.tamanhos
        form.alinhamentos.data = data.alinhamentos
        return(render_template('form.html',form=form,action='/template/' + str(id) + '/editar',titulo=u"Editando Template",testing=app.config['TESTING']))

@app.route('/documento/adicionar',methods=['POST','GET'])
@auth.login_required(role='admin')
def documento_adicionar():
    if request.method == "POST":
        form = FormDocumento.NewDocumentoForm()
        choices = [(tpl.id,tpl.nome) for tpl in Documentos.Templates.query.with_entities(Documentos.Templates.id,Documentos.Templates.nome).order_by(Documentos.Templates.nome).all()]
        form.template.choices = choices
        if form.validate_on_submit(): #TUDO OK COM O FORM ? ADICIONAR AO BD            
            #template = Documentos.Templates(arquivo=request.files['arquivo'].filename,x=request.form['x'],y=request.form['y'],tamanhos=request.form['tamanhos'],alinhamentos=request.form['alinhamentos'],quantidade_textos=request.form['quantidade_textos'],tipo=request.form['tipo'],descricao=request.form['descricao'])
            documento = Documentos.Documentos(nome=request.form['nome'],id_template=request.form['template'],textos=request.form['textos'])
            db.session.add(documento)
            db.session.commit()
            return(redirect(url_for('documento_listar')))
        else: #Se o formulário não estiver preenchido corretamente
            return(render_template('form.html',form=form,action='/documento/adicionar',titulo=u"Adicionar novo Documento",testing=app.config['TESTING']))
    else:     #Se o método for o get, abrir o formulário
        form = FormDocumento.NewDocumentoForm()
        choices = [(tpl.id,tpl.nome) for tpl in Documentos.Templates.query.with_entities(Documentos.Templates.id,Documentos.Templates.nome).order_by(Documentos.Templates.nome).all()]
        form.template.choices = choices
        logging.error(choices)
        return (render_template('form.html',form=form,action='/documento/adicionar',titulo=u"Adicionar novo Documento",testing=app.config['TESTING']))

@app.route('/documento/listar',methods=['GET'])
@auth.login_required(role='admin')
def documento_listar():
    data = Documentos.Documentos.query.order_by(Documentos.Documentos.create_date).all()
    return(render_template('documentos.html',data=data,testing=app.config['TESTING'],titulo='Lista de Documentos'))


@app.route('/documento/<id>/excluir',methods=['GET','POST'])
@auth.login_required(role='admin')
def documento_excluir(id):
    Documentos.Documentos.query.filter(Documentos.Documentos.id==int(id)).delete()
    db.session.commit()
    return(redirect(url_for('documento_listar')))

@app.route('/documento/<id>/editar',methods=['GET','POST'])
@auth.login_required(role='admin')
def documento_editar(id):
    form = FormDocumento.NewDocumentoForm()
    choices = [(tpl.id,tpl.nome) for tpl in Documentos.Templates.query.with_entities(Documentos.Templates.id,Documentos.Templates.nome).order_by(Documentos.Templates.nome).all()]
    form.template.choices = choices
    if request.method == "POST": #gravando alterações    
        if form.validate_on_submit():
            documento = Documentos.Documentos.query.get(int(id))
            documento.textos = request.form['textos']
            documento.nome = request.form['nome']
            documento.id_template=request.form['template']
            db.session.commit()
            return(redirect(url_for('documento_listar')))
        else:
            return(render_template('form.html',form=form,action='/documento/' + str(id) + '/editar',titulo=u"Editando Documento",testing=app.config['TESTING']))            
    else: #abrindo página de edição
        data = Documentos.Documentos.query.filter_by(id=int(id)).first()
        form.textos.data = data.textos
        form.template.data = data.id_template
        return(render_template('form.html',form=form,action='/documento/' + str(id) + '/editar',titulo=u"Editando Documento",testing=app.config['TESTING']))

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=80, url_prefix='/web')
