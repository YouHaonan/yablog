# -*- coding: utf-8 -*-


from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, whooshee
from flask import url_for


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(str(password))

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


tagging = db.Table('tagging',
                   db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                   db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                   )


@whooshee.register_model('title')
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=tagging, back_populates='posts')
    photos = db.relationship('Photo', back_populates='post', cascade='all, delete-orphan')

    @staticmethod
    def to_json(self):
        tags = [tag.name for tag in self.tags]
        json_post = {
            'name':'post',
            'url': url_for('api.get_post', id=self.id),
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'timestamp': self.timestamp,
            'tags': tags,
            'tags_url': url_for('api.get_post_tags', id=self.id),
            'tag_count': len(tags),
            'comments_url': url_for('api.get_post_comments', id=self.id),
            'comment_count': len(self.comments)
        }
        return json_post


@whooshee.register_model('name')
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    posts = db.relationship('Post', secondary=tagging, back_populates='tags')

    def to_json(self):
        json_tag = {
            'name':'tag',
            'url': url_for('api.get_tag', id=self.id),
            'name': self.name,
            'id': self.id,
            'posts_url': url_for('api.get_tag_posts', id=self.id),
        }
        return json_tag


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')
    floor = db.Column(db.Integer)
    replies = db.relationship('Reply', back_populates='comment', cascade='all')

    def to_json(self):
        json_comment = {
            'name':'comment',
            'url': url_for('api.get_comment', id=self.id),
            'post_url': url_for('api.get_post', id=self.post_id),
            'post_title': self.post.title,
            'post_id': self.post.id,
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp,
            'author': self.author,
            'from_admin': self.from_admin,
            'is_read':self.is_read,
            'floor': self.floor,
            'reply_count': len(self.replies)
        }
        return json_comment


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    to = db.Column(db.String(30))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    comment = db.relationship('Comment', back_populates='replies')

    def to_json(self):
        json_comment = {
            'name': 'reply',
            'url': url_for('api.get_comment', id=self.id),
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp,
            'author': self.author,
            'to': self.to,
            'comment_body': self.comment.body,
            'comment_id': self.comment.id,
            'post_id': self.comment.post.id,
            'from_admin': self.from_admin,
            'is_read': self.is_read,
        }
        return json_comment


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='photos')
