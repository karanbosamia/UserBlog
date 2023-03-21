# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret@@###!!@@(*@Karan'
cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:8081"}}, supports_credentials=True)
DB_URL = "sqlite:///userblog.sqlite3"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)
