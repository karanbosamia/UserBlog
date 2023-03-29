#!/usr/bin/env python
# encoding: utf-8
import base64
from urllib.parse import urljoin
import io
from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_cors import cross_origin
from sqlalchemy_utils.functions import database_exists
import hashlib
from models.blog_users import BlogUsers, BlogPost, Follow
from models.user_session import UserSession
from db import db, app, DB_URL



@app.route('/logout', methods=["POST"])
@cross_origin(supports_credentials=True)
def logout():
    if request.method == 'POST':
        try:
            db.session.query(UserSession).delete()
            db.session.commit()
            return jsonify(status='loggedOut')
        except:
            db.session.rollback()
            return jsonify(status='failure')

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
                    return jsonify({'status': 'Invalid Password'})
                else:
                    new = UserSession().query.filter_by(status='active').all()
                    if len(new) != 0:
                        try:
                            db.session.query(UserSession).delete()
                            db.session.commit()
                        except:
                            db.session.rollback()
                    db.session.add(UserSession(user_id=user.query.filter_by(username=username).first().id, status='active'))
                    db.session.commit()
                    return jsonify({'status': 'success', 'username': username})
            else:
                db.session.add(BlogUsers(username=username, password=password_hash))
                db.session.commit()
                return jsonify({
                    'status': 'Newly registered user'
                })
        else:
            return jsonify({'status': 'Invalid Submission'})

@app.route('/postapost', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def add_post():
    post_name = request.form.get('name', '')
    caption = request.form.get('caption', '')
    file_store = request.files.get('image', False)
    session_user = UserSession().query.filter_by(status='active').first()
    db.session.add(BlogPost(name=post_name, caption=caption, image=file_store.read(), user_id=session_user.user_id))
    db.session.commit()
    return jsonify({
        'status': 'Post added'
    })

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
    session_user = UserSession().query.filter_by(status='active').first()
    if session_user:
        test_user = user.query.get(session_user.user_id)
    if test_user:
        return test_user.profile_picture


@app.route('/get/followerposts', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def get_follower_posts():
    post = BlogPost()
    user = BlogUsers()
    base_url = 'http://localhost:8081/'
    session_user = UserSession().query.filter_by(status='active').first()
    following_ids = [following.follower_id for following in user.query.get(session_user.user_id).followed_ids if following.follower_id]
    follower_posts = {}
    for following in following_ids:
        following_user_iter = user.query.get(following)
        posts = post.query.filter_by(user_id=following_user_iter.id).all()
        # Create a URL for the data stream using the base URL of your server
        if posts:
            follower_posts[following_user_iter.username] = {post_iter.name: {
                    'name': following_user_iter.username,
                    'image': urljoin(
                        base_url, f'data:image/jpeg;base64,{base64.b64encode(io.BytesIO(post_iter.image).getvalue()).decode("utf-8")}'
                    ),
                    'caption': post_iter.caption
                } for post_iter in posts
            }
    return follower_posts

@app.route('/get/posts', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def get_posts():
    post = BlogPost()
    session_user = UserSession().query.filter_by(status='active').first()
    posts = post.query.filter_by(user_id=session_user.user_id).all()
    # Create a URL for the data stream using the base URL of your server
    base_url = 'http://localhost:8081/'
    user_posts = {post_iter.name: {
            'image': urljoin(
                base_url, f'data:image/jpeg;base64,{base64.b64encode(io.BytesIO(post_iter.image).getvalue()).decode("utf-8")}'
            ),
            'caption': post_iter.caption
        } for post_iter in posts
    }
    return user_posts

@app.route('/api/follow/<user_id>', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def follow_user(user_id):
    user = BlogUsers()
    session_user = UserSession().query.filter_by(status='active').first()
    if session_user:
        test_user = user.query.get(session_user.user_id)
    else:
        return jsonify({
            'status': 'Please log in'
        })
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
            new_follow = Follow(followed_id=new_following.id, follower_id=test_user.id)
            db.session.add(new_follow)
            db.session.commit()
            response = jsonify({
                'success': True,
                'followingId': new_follow.followed_id
            })
    return response

@app.route('/api/unfollow/<user_id>', methods=['DELETE'])
@cross_origin(supports_credentials=True)
def unfollow_user(user_id):
    user = BlogUsers()
    response = jsonify({'success': True})
    session_user = UserSession().query.filter_by(status='active').first()
    if session_user:
        test_user = user.query.get(session_user.user_id)
    else:
        return jsonify({
            'status': 'Please log in'
        })
    if test_user:
        remove_followed = Follow.query.filter_by(
            follower_id=test_user.id, followed_id=int(user_id)
        )
        if remove_followed.first():
            test_user.follower_ids.remove(remove_followed.first())
            db.session.commit()
    if int(user_id) == test_user.id:
        return jsonify({
            'status': "You can't unfollow yourself"
        })
    return response

@app.route('/get/followers', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def get_followers():
    user = BlogUsers()
    session_user = UserSession().query.filter_by(status='active').first()
    if session_user:
        test_user = user.query.get(session_user.user_id)
    else:
        return jsonify({
            'status': 'Please log in'
        })
    follower_ids = [following.followed_id for following in test_user.follower_ids if following.followed_id]
    follower_usernames = []
    for follower in follower_ids:
        if follower:
            follower_usernames.append(
                {
                    "id": follower,
                    "username": user.query.get(follower).username
                }
            )
    return follower_usernames

@app.route('/get/following', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def get_followings():
    user = BlogUsers()
    session_user = UserSession().query.filter_by(status='active').first()
    if session_user:
        test_user = user.query.get(session_user.user_id)
    else:
        return jsonify({
            'status': 'Please log in'
        })
    following_ids = [following.follower_id for following in test_user.followed_ids if following.follower_id]
    following_usernames = []
    for following in following_ids:
        if following:
            following_usernames.append(
                {
                    "id": following,
                    "username": user.query.get(following).username
                }
            )
    return following_usernames

@app.route('/api/following', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_following():
    user = BlogUsers()
    session_user = UserSession().query.filter_by(status='active').first()
    if session_user:
        test_user = user.query.get(session_user.user_id)
    else:
        return jsonify({
            'status': 'Please log in'
        })
    if test_user:
        followed_ids = [following.follower_id for following in test_user.followed_ids if following.follower_id]
        follower_ids = [following.followed_id for following in test_user.follower_ids if following.followed_id]
        data_response = jsonify({
            'followed_ids': followed_ids,
            'follower_ids': follower_ids
        })
    else:
        followed_ids = []
        follower_ids = []
        data_response = jsonify({
            'followed_ids': followed_ids,
            'follower_ids': follower_ids
        })
    return data_response

if __name__ == "__main__":
    if not database_exists(DB_URL):
        with app.app_context():
            db.create_all()
    app.run(port=8080, debug=True)
