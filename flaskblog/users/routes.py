from flask import request, Blueprint, jsonify
from flaskblog import db, bcrypt
from flaskblog.models import User, token_required
from .auth_helper import Auth
from .utils import get_all_users, get_a_user, getOtpApi
import validators
from .forms import RegistrationForm
from flask import session
from werkzeug.security import generate_password_hash

users = Blueprint('users', __name__)


@users.route("/users/register", methods=['GET', 'POST'])
def register():
    req = request.get_json()
    form = RegistrationForm().from_json(req)
    if not form.validate():
        # if len(new_user.password) < 6:
        #     return jsonify({'error': "Password is too short"})
        # if len(new_user.username) < 3:
        #     return jsonify({"error": "Username is too short"})
        # if not new_user.username.isalnum() or " " in new_user.username:
        #     return jsonify({"error": "Username should be alphanumeric, also no spaces"})
        # if not validators.email(new_user.email):
        #     return jsonify({"error": "Email is not valid"})
        # if User.query.filter_by(username=request.json.get('username')).first():
        #     return jsonify({"error": "Username is taken"})
        # if User.query.filter_by(email=request.json.get('email')).first():
        #     return jsonify({"error": "Email is taken"})
        response_object = {
            'status': 'danger',
            'message': form.errors
        }
        return response_object
    hashed_password = generate_password_hash(form.password.data)
    new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    response_object = {
        'status': 'success',
        'message': 'User created',
    }
    return response_object


@users.route('/users/list', methods=['GET', 'POST'])
@token_required
def list_of_all_users(a):
    user_list = get_all_users()
    return jsonify(user_list)


@users.route('/users/user_profile/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id=None):
    """get a user given its identifier"""
    user = get_a_user(user_id)
    if not user:
        users.abort(404)
    else:
        return user


@users.route("/users/login", methods=['GET', 'POST'])
def login():
    return Auth.login_user()


@users.route("/users/logout")
def logout():
    return Auth.logout_user()


@users.route("/users/account/<int:user_id>/update", methods=['GET', 'POST'])
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


@users.route('/users/follow/<username>')
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


@users.route('/users/unfollow/<username>')
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


@users.route("/users/user_list_followers/<username>")
@token_required
def listFollowers(a, username):
    user = User.query.filter_by(username=username).first_or_404()
    user_followers = user.followers.all()
    response_data = {
        'status': 'success',
        'message': 'Your followers list is: ' + str(user_followers) + '.'
    } 
    return response_data


@users.route("/users/user_list_following/<username>")
@token_required
def listFollowing(a, username):
    user = User.query.filter_by(username=username).first_or_404()
    user_following = user.followed.all()
    response_data = {
        'status': 'success',
        'message': 'Your following list is: ' + str(user_following) + '.'
    } 
    return response_data


@users.route("/users/follower/<int:user_id>/delete", methods=['GET', 'POST'])
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


@users.route("/users/get_otp", methods=['POST'])
def get_otp():
    num = request.json.get('number')
    val = getOtpApi(num)
    if val:
        return jsonify({'message': 'otp sent in your mobile number'})


@users.route('/users/validateOtp', methods=['POST'])
def validateOtp():
    otp = request.json.get('otp')
    if 'response' in session:
        s = session['response']
        session.pop('response', None)
        if s == otp:
            return jsonify({'message': 'You are Authorized, Thank You.'})
        else:
            return jsonify({'message': 'You are not Authorized, Sorry!!'})
    return jsonify({"message": "Sorry, OTP expired please resend the otp."})
