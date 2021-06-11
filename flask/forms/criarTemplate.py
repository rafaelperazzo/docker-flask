from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import *
from wtforms.validators import DataRequired,Email,Length,ValidationError,InputRequired,EqualTo,Optional

def validate_vetor(form,field):
    dados = field.data
    dados = dados.split(sep=';')
    try:
        inteiros = list(map(int,dados))   
    except:
        raise ValidationError("Vetor incorreto!")

def validate_quantidade(form,field):
    dados = field.data
    dados = dados.split(sep=';')
    inteiros = list(map(int,dados))
    quantidade_textos = int(form.quantidade_textos.data)
    if (len(inteiros)!=quantidade_textos):
        raise ValidationError("A quantidade deve ser igual a quantidade de textos!")

def validate_file(form,field):
    if form.tipo.data=='0':
        form.arquivo.flags.required = True
    else:
        form.arquivo.flags.required = False
    if form.arquivo.data=='' and form.tipo.data=='0':
        raise ValidationError('Escolha o arquivo!')

class NewTemplateForm(FlaskForm):
    tipo = SelectField(u'Tipo de Template: ',choices=[('0','PNG'),('1','HTML')],validators=[DataRequired()])
    nome = StringField('Nome do template: ', validators=[DataRequired()])
    descricao = TextAreaField(u'Descrição do template: ', validators=[DataRequired()])
    arquivo = FileField(u'Arquivo de template',description='Apenas para o tipo PNG',validators=[])
    quantidade_textos = IntegerField('Quantidade de textos: ', validators=[InputRequired()])
    x = StringField('Vetor X: ', validators=[InputRequired(),validate_vetor,validate_quantidade])
    y = StringField('Vetor Y: ', validators=[InputRequired(),validate_vetor,validate_quantidade])
    tamanhos = StringField('Vetor Tamanhos: ', validators=[InputRequired(),validate_vetor,validate_quantidade])
    alinhamentos = StringField('Vetor Alinhamentos: ', validators=[InputRequired(),validate_vetor,validate_quantidade])
    submit = SubmitField('Enviar',validators=[validate_file])