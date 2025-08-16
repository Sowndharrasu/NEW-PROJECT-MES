from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required
from models_mongo import UserDoc
from forms import LoginForm

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        user = UserDoc.objects(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f"Welcome, {user.username}!", "success")
            return redirect(url_for("main.index"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/bootstrap-admin")
def bootstrap_admin():
    admin = UserDoc.objects(username="admin").first()
    if not admin:
        admin = UserDoc(username="admin", email="admin@company.com", role="Admin")
        admin.set_password("admin123")
        admin.save()
        return "✅ Admin created: admin / admin123"
    return "ℹ Admin already exists"
