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
    profile_picture = db.Column(db.LargeBinary, nullable = True)
    followed_ids = db.relationship(
        "Follow", back_populates="followed", foreign_keys='Follow.followed_id'
    )
    follower_ids = db.relationship(
        "Follow", back_populates="follower", foreign_keys='Follow.follower_id'
    )


class BlogPost(db.Model):
    __tablename__ = 'blog_post'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), nullable=False)
    caption = db.Column(db.String(250))
    image = db.Column(db.LargeBinary, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey("blog_users.id"))


class Follow(db.Model):
    __tablename__ = "follows"

    id = db.Column(db.Integer, primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("blog_users.id"))
    follower_id = db.Column(db.Integer, db.ForeignKey("blog_users.id"))
    # making sure (followed_id, follower_id) are unique
    db.UniqueConstraint(followed_id, follower_id)

    follower = db.relationship("BlogUsers", foreign_keys=[follower_id])
    followed = db.relationship("BlogUsers", foreign_keys=[followed_id])
