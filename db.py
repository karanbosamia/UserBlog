# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret@@###!!@@(*@Karan'

DB_URL = "sqlite:///userblog.sqlite3"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)
