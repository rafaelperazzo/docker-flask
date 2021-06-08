from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import *
from wtforms.validators import DataRequired,Email,Length,ValidationError,InputRequired,EqualTo

class NewTemplateForm(FlaskForm):
    arquivo = StringField('Nome: ', validators=[DataRequired()])
    submit = SubmitField('Enviar')