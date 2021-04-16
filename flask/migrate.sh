export FLASK_APP=root.py
#flask db init
flask db migrate -m "Initial migration."
flask db upgrade
