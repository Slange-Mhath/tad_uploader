import functools
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from tad_uploader import db


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login')
def login():
    return render_template('auth/login.html')


@bp.route('/signup')
def signup():
    return render_template('auth/signup.html')


@bp.route('/signup', methods=('GET', 'POST'))
def signup_post():
    email = request.form.get('email')
    username = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(
        email=email, username=username).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@bp.route('/login', methods=('GET', 'POST'))
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('index'))


def profile():
    return render_template('/', name=current_user.name)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


