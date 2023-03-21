#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_cors import cross_origin
from sqlalchemy_utils.functions import database_exists
import hashlib
from models.blog_users import BlogUsers, BlogPost, Follow
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

@app.route('/api/get/users', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_users():
    user = BlogUsers()
    test_user = user.query.all()
    users = []
    for user in test_user:
        users.append({
            'id': user.id,
            'username': user.username
        })
    return users

@app.route('/get/profile', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def get_profile():
    user = BlogUsers()
    test_user = user.query.filter_by(username='karan1').first()
    return test_user.profile_picture

@app.route('/api/follow/<user_id>', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def follow_user(user_id):
    user = BlogUsers()
    test_user = user.query.filter_by(username='karan1').first()
    response = jsonify({
        'status': 'success'
    })
    if int(user_id) == test_user.id:
        return jsonify({
            'status': "You can't folow yourself"
        })
    else:
        new_following = False
        if user_id and isinstance(user_id, str):
            new_following = user.query.filter_by(id=int(user_id)).first()
        if new_following:
            new_follow = Follow(follower_id=new_following.id, followed_id=test_user.id)
            db.session.add(new_follow)
            db.session.commit()
            response = jsonify({
                'success': True,
                'followingId': new_follow.follower_id
            })    
    return response

@app.route('/api/unfollow/<user_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def unfollow_user(user_id):
    user = BlogUsers()
    response = jsonify({'success': True})
    test_user = user.query.filter_by(username='karan1').first()
    if test_user:
        remove_follower = Follow.query.filter_by(
            followed_id=test_user.id, follower_id=int(user_id)
        )
        if remove_follower.first():
            test_user.followed_ids.remove(remove_follower.first())
            db.session.commit()
    if int(user_id) == test_user.id:
        return jsonify({
            'status': "You can't unfolow yourself"
        })
    return response

@app.route('/get/followers', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def get_followers():
    user = BlogUsers()
    test_user = user.query.filter_by(username='karan1').first()
    return test_user.profile_picture

@app.route('/api/following', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_following():
    user = BlogUsers()
    test_user = user.query.filter_by(username='karan1').first()
    followers = []
    following = []
    if test_user:
        followed_ids = [following.follower_id for following in test_user.followed_ids]
    else:
        followed_ids = []
    return followed_ids

if __name__ == "__main__":
    if not database_exists(DB_URL):
        with app.app_context():
            db.create_all()
    app.run(port=8080, debug=True)
