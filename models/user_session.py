# -*- coding: utf-8 -*-

from db import db

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

class UserSession(db.Model):
    __tablename__ = 'user_session'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('blog_users.id'))
