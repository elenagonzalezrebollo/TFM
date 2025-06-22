from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.auth.forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__, template_folder="../templates")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated: return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and user.verify(form.password.data):
            login_user(user)
            flash("Sesión iniciada!", "success")
            return redirect(url_for("main.dashboard"))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("login.html", form=form)

@auth_bp.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated: return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data.lower()).first():
            flash("Nombre de usuario ya existe.", "warning")
        else:
            user = User(username=form.username.data.lower())
            user.password = form.password.data
            db.session.add(user); db.session.commit()
            flash("¡Cuenta creada! Inicia sesión.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("auth.login"))
