# -*- coding: utf-8 -*-

from db import db

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


class BlogUsers(db.Model):
    __tablename__ = 'blog_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    name = db.Column(db.String(256))
    password = db.Column(db.String(256))

