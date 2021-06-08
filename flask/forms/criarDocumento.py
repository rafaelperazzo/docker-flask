from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import *
from wtforms.validators import DataRequired,Email,Length,ValidationError,InputRequired,EqualTo

class NewDocumentoForm(FlaskForm):
    textos = TextAreaField('Vetor Textos: ', validators=[DataRequired()])
    x = StringField('Vetor X: ', validators=[DataRequired()])
    y = StringField('Vetor Y: ', validators=[DataRequired()])
    tamanhos = StringField('Vetor Tamanhos: ', validators=[DataRequired()])
    alinhamentos = StringField('Vetor Alinhamentos: ', validators=[DataRequired()])
    submit = SubmitField('Enviar')