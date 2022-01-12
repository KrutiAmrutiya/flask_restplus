import os
import secrets
from PIL import Image
from flask import url_for, current_app, session
from flask_mail import Message
from flaskblog import mail
from flaskblog.models import Post, User
import random
from twilio.rest import Client


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



def generateOtp():
    return random.randrange(100000, 999999)


def getOtpApi(num):
    account_sid = 'ACe431e8fc8b41c9a97af4e3c2b9d01b0d'
    auth_token = '2a37dfa3d9050f8e1be197a4215eb35c'
    client = Client(account_sid, auth_token)
    otp = generateOtp()
    body = "Your OTP is " + str(otp)
    session['response'] = str(otp)
    message = client.messages \
        .create(
            body=body,
            from_='+19592155506',
            to=num
        )
    if message.sid:
        return True
    else:
        return False