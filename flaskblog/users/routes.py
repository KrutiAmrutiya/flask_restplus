from flask import request, Blueprint, jsonify
from flaskblog import db
from flaskblog.models import User, token_required
from .auth_helper import Auth
from .utils import get_all_users, get_a_user

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    user = User.query.filter_by(email=request.json.get('email')).first()
    if not user:
        new_user = User(
            username=request.json.get('username'),
            email=request.json.get('email'),
            password=request.json.get('password')
        )
        print(new_user)
        db.session.add(new_user)
        db.session.commit()
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return response_object, 409


@users.route('/user/list', methods=['GET', 'POST'])
def list_of_all_users():
    user_list = get_all_users()
    return jsonify(user_list)


@users.route('/user_profile/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id=None):
    """get a user given its identifier"""
    user = get_a_user(user_id)
    if not user:
        users.abort(404)
    else:
        return user


@users.route("/login", methods=['GET', 'POST'])
def login():
    return Auth.login_user()


@users.route("/logout")
def logout():
    return Auth.logout_user()


@users.route("/account/<int:user_id>/update", methods=['GET', 'POST'])
@token_required
def account(a, user_id=None):
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.username=request.json.get('username'),
        user.email=request.json.get('email'),
        user.id=request.json.get('id'),
        user.password=request.json.get('password')
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Your account is updated.',
        }
        return jsonify(response_object)


@users.route('/follow/<username>')
@token_required
def follow(current_user, username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        response_data = {
            'status': 'danger',
            'message': 'User %s not found.' % username
        }
        return response_data
    if user == current_user:
        response_data = {
            'status': 'danger',
            'message': 'You can\'t follow yourself!'
        }
        return response_data
    u = current_user.follow(user)
    if u is None:
        response_data = {
            'status': 'danger',
            'message': 'Cannot follow ' + username + '.'
        }
        return response_data
    db.session.add(u)
    db.session.commit()
    response_data = {
        'status': 'success',
        'message': 'You are now following ' + username + '!'
    } 
    return response_data


@users.route('/unfollow/<username>')
@token_required
def unfollow(current_user, username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        response_data = {
            'status': 'danger',
            'message': 'User %s not found.' % username
        }
        return response_data
    if user == current_user:
        response_data = {
            'status': 'danger',
            'message': 'You can\'t unfollow yourself!'
        }
        return response_data
    u = current_user.unfollow(user)
    if u is None:
        response_data = {
            'status': 'danger',
            'message': 'Cannot unfollow ' + username + '.'
        }
        return response_data
    db.session.add(u)
    db.session.commit()
    response_data = {
        'status': 'success',
        'message': 'You have stopped following ' + username + '.'
    } 
    return response_data


@users.route("/userListFollowers/<username>")
@token_required
def listFollowers(a, username):
    user = User.query.filter_by(username=username).first_or_404()
    user_followers = user.followers.all()
    response_data = {
        'status': 'success',
        'message': 'Your followers list is: ' + str(user_followers) + '.'
    } 
    return response_data


@users.route("/userListFollowing/<username>")
@token_required
def listFollowing(a, username):
    user = User.query.filter_by(username=username).first_or_404()
    user_following = user.followed.all()
    response_data = {
        'status': 'success',
        'message': 'Your following list is: ' + str(user_following) + '.'
    } 
    return response_data


@users.route("/user_profile/<int:user_id>/delete", methods=['GET', 'POST'])
@token_required
def removeFollower(current_user, user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    unfollow = user.unfollow(current_user)
    db.session.add(unfollow)
    db.session.commit()
    response_data = {
        'status': 'success',
        'message': 'Your follower has been removed!'
    } 
    return response_data
