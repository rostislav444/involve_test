from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = True

try:
    from local_settings import *
except:
    from peewee import SqliteDatabase
    db = SqliteDatabase('database.db')

