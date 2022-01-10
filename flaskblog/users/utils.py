import os
import secrets
from PIL import Image
from flask import url_for, current_app, request
from flask.json import jsonify
from flask_mail import Message
from flaskblog import mail, db
from flaskblog.models import Post, User, PostLike
import datetime
from flask_login import current_user


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


def json(self):
    return {'id': self.id, 'username': self.username, 'email': self.email}


def json_post(self):
    return {'id': self.id, 'title': self.title, 'content': self.content, 'date_posted': self.date_posted}


def get_all_users():
    return [json(user) for user in User.query.all()]


def get_a_user(user_id):
    return json(User.query.filter_by(id=user_id).first())


def get_all_posts():
    return [json_post(post) for post in Post.query.all()]


def get_a_post(post_id):
    return json_post(Post.query.filter_by(id=post_id).first())
