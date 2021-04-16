from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import *
from wtforms.validators import DataRequired,Email,Length,ValidationError,InputRequired

def validar_username(form,field):
        if len(field.data)>1:
            raise ValidationError('Erro!')

class NewUserForm(FlaskForm):
    name = StringField('Nome: ', validators=[DataRequired()])
    username = StringField('Nome de usuário: ',validators=[InputRequired(),validar_username])
    email = EmailField('E-mail: ', validators=[DataRequired(),Email(check_deliverability=True)])
    password = PasswordField('Password: ', validators=[DataRequired()])
    confirmar_password = PasswordField('Confirmar password: ',validators=[DataRequired()])
    submit = SubmitField('Enviar')

    