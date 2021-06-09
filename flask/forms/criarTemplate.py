from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import *
from wtforms.validators import DataRequired,Email,Length,ValidationError,InputRequired,EqualTo

class NewTemplateForm(FlaskForm):
    tipo = SelectField(u'Tipo de Template: ',choices=[('0','PNG'),('1','HTML')])
    nome = StringField('Nome do template: ', validators=[DataRequired()])
    descricao = TextAreaField(u'Descrição do template: ', validators=[DataRequired()])
    arquivo = FileField(u'Arquivo de template',description='Apenas para o tipo PNG')
    quantidade_textos = IntegerField('Quantidade de textos: ', validators=[DataRequired()])
    x = StringField('Vetor X: ', validators=[DataRequired()])
    y = StringField('Vetor Y: ', validators=[DataRequired()])
    tamanhos = StringField('Vetor Tamanhos: ', validators=[DataRequired()])
    alinhamentos = StringField('Vetor Alinhamentos: ', validators=[DataRequired()])
    submit = SubmitField('Enviar')