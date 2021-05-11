# FLASK com DOCKER e MYSQL
** aplicação base em flask com mysql com docker e docker-compose **

## Requisitos

* [Docker](https://docs.docker.com/get-docker)
* [Docker-compose](https://docs.docker.com/compose/install/)

## Entrada

* Arquivo com senhas em flask/config.ini, conforme modelo abaixo
* Arquivo(s) com fontes true type em fonts/
* Criar pasta mysql/

```
[DEFAULT]
testing = 1
secret_key = 
working_dir = /flask/
font_path = /fonts/Times_New_Roman_Bold.ttf
theme = cerulean
log_file = app.log
log_write = w
log_type = 10

[DB]
db_user = root
db_database = flask
db_host = db_flask
db_password = 

[EMAIL]
mail_server = smtp.gmail.com
mail_port = 465
mail_username = 
mail_password = 
```

## Saída

* http://host:8000

## Como executar

```
docker-compose up -d
```

## Autor

* Prof. Rafael Perazzo Barbosa Mota ( rafael.mota (at) ufca.edu.br )
