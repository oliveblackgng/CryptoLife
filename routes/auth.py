
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from email_validator import validate_email, EmailNotValidError

from extensions import db
from models.user import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please complete all fields.", "error")
            return redirect(url_for("auth.register"))

        if len(username) > 80 or len(password) < 8:
            flash("Username is too long or password is too short.", "error")
            return redirect(url_for("auth.register"))

        try:
            validate_email(email)
        except EmailNotValidError:
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already registered.", "error")
            return redirect(url_for("auth.register"))

        user = User(
            username=username,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash("Your CryptoLife account has been created!", "success")

        return redirect(url_for("dashboard.home"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):

            login_user(user)

            flash("Welcome back!", "success")

            return redirect(url_for("dashboard.home"))

        flash("Incorrect email or password.", "error")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("You have logged out.", "success")

    return redirect(url_for("auth.login"))
