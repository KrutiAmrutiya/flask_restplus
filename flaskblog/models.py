from datetime import datetime
from flask.json import jsonify
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, jsonify, session
from werkzeug.wrappers import auth
from flaskblog.config import Config
from flaskblog import db, login_manager
from flask_login import UserMixin
from functools import wraps 
import jwt


followers = db.Table('followers',
                    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(100), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    liked = db.relationship('PostLike', foreign_keys='PostLike.user_id', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy=True)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.date_posted.desc())

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id=self.id, post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id, PostLike.post_id == post.id).count() > 0


    @staticmethod
    def decode_auth_token():
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            # if 'X-API-KEY' in request.headers:
            #     auth_token = request.headers['X-API-KEY']
            if 'token' in session:
                s = session['token']
                session.pop('token', None)
                return jsonify({'message': 'You are suceesfuly loged out, Thank You.'})
            return jsonify({'message': 'You are not loged out, Sorry!!'})

            # payload = jwt.decode(auth_token, Config.SECRET_KEY)
            # response_object = {
            #             'status': 'success',
            #             'message': 'Successfully logged out.',
            #             'Authorization': payload
            # }
            # return jsonify(response_object)
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='article', lazy='dynamic')
    updated_date = db.Column(db.DateTime, nullable=True)

    def get_comments(self):
        return Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc())

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    body = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Comment('{self.body}')"

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        # token = None

        # if 'X-API-KEY' in request.headers:
        #     token = request.headers['X-API-KEY']
        if 'token' in session:
            token = session['token']

        else:
            return jsonify({'message': 'Already loged out, Please log in again.'})

        try:
            data = jwt.decode(token, Config.SECRET_KEY)
            current_user = User.query.filter_by(id=data['public_id']).first()
        except:
            return jsonify({'message': 'Invalid token.'})

        return f(current_user, *args, **kwargs)
    return decorator
