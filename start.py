# -*- coding: utf-8 -*-


import os

import click

from app.models import Admin, Post, Comment, Tag
from app import create_app, db
from app.fakes import fake_comments, fake_posts, fake_tags

app = create_app(os.getenv('FLASK_CONFIG') or 'development')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Admin=Admin, Tag=Tag, Post=Post, Comment=Comment)


@app.cli.command()
@click.option('--tag', default=45, help='Quantity of tags, default is 45.')
@click.option('--post', default=50, help='Quantity of posts, default is 50.')
@click.option('--comment', default=500, help='Quantity of comments, default is 500.')
def forge(tag, post, comment):
    click.echo('Generating %d tags...' % tag)
    fake_tags(tag)

    click.echo('Generating %d posts...' % post)
    fake_posts(post)

    click.echo('Generating %d comments...' % comment)
    fake_comments(comment)
    click.echo('Done.')

