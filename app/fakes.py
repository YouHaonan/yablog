# -*- coding: utf-8 -*-

import random

from faker import Faker

from . import db
from .models import Post, Comment, Tag
from sqlalchemy.exc import IntegrityError

fake = Faker('zh_CN')


def fake_tags(count=45):
    for i in range(count):
        tag = Tag(name=fake.word())
        db.session.add(tag)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            timestamp=fake.date_time_this_year()
        )
        for j in range(random.randint(1, 5)):
            tag = Tag.query.get(random.randint(1, Tag.query.count()))
            if tag not in post.tags and tag is not None:
                post.tags.append(tag)
        db.session.add(post)
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

