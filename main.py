#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_cors import cross_origin
from sqlalchemy_utils.functions import database_exists
import hashlib
from models.blog_users import BlogUsers, BlogPost
from db import db, app, DB_URL


@app.route('/fetchdata', methods=["GET", "POST"])
@cross_origin(supports_credentials=True)
def login():
    if request.method == 'GET':
        return {
            'status': 'success'
        }
        return render_template("index.html")
    elif request.method == 'POST':
        if request.form.get("username"):
            username = request.form["username"]
        if request.form.get("password"):
            password = request.form["password"]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = BlogUsers()
        if request.form.get('username', False) and request.form.get('password', False):
            if user.query.filter_by(username=username).first():
                if user.query.filter_by(username=username).first().password != password_hash:
                    return jsonify({'status': 'error'})
                else:
                    return jsonify({'status': 'success', 'username': username})
            else:
                db.session.add(BlogUsers(username=username, password=password_hash))
                db.session.commit()
                return jsonify({'status':'New addition of user'})
        else:
            return jsonify({'status': 'Invalid Submission'})

@app.route('/postapost', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def add_post():
    post_name = request.form.get('name', '')
    caption = request.form.get('caption', '')
    file_store = request.files.get('image', False)
    db.session.add(BlogPost(name=post_name, caption=caption, image=file_store.read()))
    db.session.commit()
    return True


if __name__ == "__main__":
    if not database_exists(DB_URL):
        with app.app_context():
            db.create_all()
    app.run(port=8080, debug=True)
