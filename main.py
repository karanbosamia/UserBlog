#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy_utils.functions import database_exists
import hashlib
from models.blog_users import BlogUsers
from db import db, app, DB_URL


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = BlogUsers()
        if user.query.filter_by(username=username).first():
            if user.query.filter_by(username=username).first().password != password_hash:
                raise Exception("Invalid password")
            pass
        else:
            db.session.add(BlogUsers(username=username, password=password_hash))
            db.session.commit()
        return render_template("login.html")


if __name__ == "__main__":
    if not database_exists(DB_URL):
        with app.app_context():
            db.create_all()
    app.run(port=8080)
