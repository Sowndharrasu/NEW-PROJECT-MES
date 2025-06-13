from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app import db
from models import User
from forms import LoginForm
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/create-admin')
def create_admin():
    """Create default admin user if none exists"""
    admin = User.query.filter_by(role='Admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            email='admin@company.com',
            role='Admin'
        )
        admin_user.set_password('admin123')  # Change this in production
        db.session.add(admin_user)
        
        # Create other default users
        manager_user = User(
            username='manager',
            email='manager@company.com',
            role='Manager'
        )
        manager_user.set_password('manager123')
        db.session.add(manager_user)
        
        operator_user = User(
            username='operator',
            email='operator@company.com',
            role='Operator'
        )
        operator_user.set_password('operator123')
        db.session.add(operator_user)
        
        storekeeper_user = User(
            username='storekeeper',
            email='storekeeper@company.com',
            role='Storekeeper'
        )
        storekeeper_user.set_password('storekeeper123')
        db.session.add(storekeeper_user)
        
        db.session.commit()
        flash('Default users created successfully! Use admin/admin123 to login.', 'success')
    else:
        flash('Admin user already exists.', 'info')
    
    return redirect(url_for('auth.login'))
