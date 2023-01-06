import datetime
import logging
import re
from datetime import timezone

from flask import Blueprint, flash, url_for, redirect, request, render_template, Request
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from data import db
from data.auth import User

auth = Blueprint("auth", __name__)
_EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

_PASSWORD_HASH_METHOD = "pbkdf2:sha256:2048"
_SALT_LENGTH = 32


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@auth.route("/signup")
def signup():
    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")

    if not _EMAIL_REGEX.fullmatch(email):
        flash("Email address {} is invalid".format(email))
        return redirect(url_for('auth.signup'))

    if not name:
        flash("Please enter a display name")
        return redirect(url_for('auth.signup'))

    if len(password) < 10:
        flash("Please use a password longer than 10 characters")
        return redirect(url_for('auth.signup'))

    if len(password) > 50:
        flash("YOUR {} LENGTH PASSWORD IS TOO POWERFUL, please use one that's within 50 characters".format(len(password)))
        return redirect(url_for('auth.signup'))

    user = User.query.filter_by(email=email).first()

    # if a user is found, we want to redirect back to signup page so user can try again
    if user:
        flash("Email address {} exists".format(email))
        return redirect(url_for("auth.login"))

    hashed_password = generate_password_hash(password, method=_PASSWORD_HASH_METHOD, salt_length=_SALT_LENGTH)

    new_user = User(email=email,
                    display_name=name,
                    password=hashed_password,
                    registered_date_utc=datetime.datetime.now(tz=timezone.utc))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    logging.info("User {} registered, id={}".format(email, new_user.id))

    return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
