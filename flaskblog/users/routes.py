from flask import app, render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post, token_required
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                    RequestResetForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture
from flaskblog.tasks import send_reset_email, reverse
from .auth_helper import Auth
from typing import Dict, Tuple
from flask_restplus import Resource
from .utils import get_all_users, get_a_user

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    # form = RegistrationForm()
    # if form.validate_on_submit():
    #     hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    #     user = User(username=form.username.data, email=form.email.data, password=hashed_password)
    #     db.session.add(user)
    #     db.session.commit()
    #     flash('Your account has been created! You are now able to log in', 'success')
    #     return redirect(url_for('users.login'))
    # return render_template('register.html', title='Register', form=form)
    # return make_response({'form':form})
    # data = {
    #     'username':request.json.get("username"),
    #     'email':request.json.get("email"),
    #     'password':request.json.get("password")
    # }
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

    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(email=form.email.data).first()
    #     if user and bcrypt.check_password_hash(user.password, form.password.data):
    #         login_user(user, remember=form.remember.data)
    #         next_page = request.args.get('next')
    #         return redirect(next_page) if next_page else redirect(url_for('main.home'))
    #     else:
    #         flash('Login Unsuccessful. Please check email and password', 'danger')
    # return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    # logout_user()
    # return redirect(url_for('main.home'))
    return Auth.logout_user()


@users.route("/account/<int:user_id>/update", methods=['GET', 'POST'])
@token_required
def account(a, user_id=None):
    # form = UpdateAccountForm()
    # if form.validate_on_submit():
    #     if form.picture.data:
    #         picture_file = save_picture(form.picture.data)
    #         current_user.image_file = picture_file
    #     current_user.username = form.username.data
    #     current_user.email = form.email.data
    #     db.session.commit()
    #     flash('Your account has been updated!', 'success')
    #     return redirect(url_for('users.account'))
    # elif request.method == 'GET':
    #     form.username.data = current_user.username
    #     form.email.data = current_user.email
    # image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    # return render_template('account.html', title='Account', image_file=image_file, form=form)
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


# @users.route("/user_profile/<int:user_id>", methods=['GET', 'POST'])
# @login_required
# def user_profile(user_id=None):
#     user = User.query.get_or_404(user_id)
#     return render_template('user_profile.html', title='User Profile', user=user)


@users.route("/user/<string:username>")
@login_required
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/process/<name>", methods=['GET', 'POST'])
def process(name):
    reverse.delay(name)
    return 'hello'


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user_email = user.email
        send_reset_email.delay(user_email)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@users.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    print(user)
    if user is None:
        flash('User %s not found.' % username, 'danger')
        return redirect(url_for('main.home'))
    if user == current_user:
        flash('You can\'t follow yourself!', 'danger')
        return redirect(url_for('users.user_profile', user_id=user.id))
    u = current_user.follow(user)
    if u is None:
        flash('Cannot follow ' + username + '.', 'danger')
        return redirect(url_for('users.user_profile', user_id=user.id))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + username + '!', 'success')
    return redirect(url_for('users.user_profile', user_id=user.id))


@users.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    print(user)
    if user is None:
        flash('User %s not found.' % username, 'danger')
        return redirect(url_for('main.home'))
    if user == current_user:
        flash('You can\'t unfollow yourself!', 'danger')
        return redirect(url_for('users.user_profile', user_id=user.id))
    u = current_user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + username + '.', 'danger')
        return redirect(url_for('users.user_profile', user_id=user.id))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + username + '.', 'success')
    return redirect(url_for('users.user_profile', user_id=user.id))


@users.route("/userListFollowers/<username>")
@login_required
def listFollowers(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_followers = user.followers.all()
    return render_template('user_profile.html', user_followers=user_followers, user=user, user_id=user.id)


@users.route("/userListFollowing/<username>")
@login_required
def listFollowing(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_following = user.followed.all()
    return render_template('user_profile.html', user_following=user_following, user=user, user_id=user.id)


@users.route("/user_profile/<int:user_id>/delete", methods=['GET', 'POST'])
@login_required
def removeFollower(user_id=None):
    user = User.query.get(user_id)
    print(user)
    unfollow = user.unfollow(current_user)
    db.session.add(unfollow)
    db.session.commit()
    flash('Your follower has been removed!', 'success')
    return redirect(request.referrer)
