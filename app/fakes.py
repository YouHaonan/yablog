# -*- coding: utf-8 -*-

import random

from faker import Faker

from . import db
from .models import Post, Comment, Tag
from sqlalchemy.exc import IntegrityError

fake = Faker('zh_CN')


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_tags(count=45):
    for i in range(count):
        tag = Tag(
            name=fake.word(),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(tag)
    db.session.commit()



def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            is_read=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            is_read=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

