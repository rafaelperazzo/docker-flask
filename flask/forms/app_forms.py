from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired

class MyForm(FlaskForm):
    name = StringField('Nome: ', validators=[DataRequired()])
    submit = SubmitField('Enviar')