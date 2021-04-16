from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import *
from wtforms.validators import DataRequired,Email,Length,ValidationError,InputRequired,EqualTo

def validar_username(form,field):
        if len(field.data)<8:
            raise ValidationError('Erro!')

class NewUserForm(FlaskForm):
    name = StringField('Nome: ', validators=[DataRequired()])
    username = StringField('Nome de usuário: ',validators=[InputRequired()])
    email = EmailField('E-mail: ', validators=[DataRequired(),Email(check_deliverability=True)])
    password = PasswordField('Password: ', validators=[InputRequired(),EqualTo('confirmar',message='As senhas devem ser iguais!'),Length(min=8,message='A senha deve ser de pelo menos 8 caracteres')])
    confirmar = PasswordField('Confirmar password: ')
    submit = SubmitField('Enviar')

    