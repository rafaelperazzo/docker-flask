from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import *
from wtforms.validators import DataRequired,Email,Length,ValidationError,InputRequired,EqualTo

class NewDocumentoForm(FlaskForm):
    textos = TextAreaField('Vetor Textos: ', validators=[DataRequired()])
    template = SelectField(u'Template: ',coerce=int)
    nome = StringField('Nome do documento: ', validators=[DataRequired()])
    submit = SubmitField('Enviar')