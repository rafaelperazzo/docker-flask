FROM python:latest
RUN apt-get update
RUN apt-get install -y g++ build-essential libmariadbclient-dev libmariadb-dev-compat libmariadb-dev
RUN pip install numpy scipy pandas sympy matplotlib werkzeug==0.16.1 Flask lxml mysqlclient unidecode requests Flask-HTTPAuth Flask-Mail Flask-Uploads pdfkit waitress bs4 PyMySQL sqlalchemy
RUN pip install semantic-version Pillow
EXPOSE 80
CMD python /flask/root.py
