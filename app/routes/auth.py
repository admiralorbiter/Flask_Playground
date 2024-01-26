from flask import Blueprint
from app.models import User
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from datetime import datetime
from werkzeug.urls import url_parse

auth = Blueprint('auth', __name__)

## Auth Routes ##  Auth Routes ##  Auth Routes ##  Auth Routes ##  Auth Routes ##  Auth Routes ##
# Login Page
# Currently Defaults to Login into Dev User
@auth.route('/login', methods=['GET', 'POST'])
def login():
    ## Remove this before production, just short way to login
    # config = 'development'
    config = 'student_dev'
    if config=='development':
        dev_user = User.query.get(1)  # Assuming user with ID 1 is your dev user
        login_user(dev_user)
        dev_user.last_login = datetime.utcnow()
        return redirect(url_for('home'))
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        user.role_id = 'user'
        login_user(user)
        user.last_login = datetime.utcnow()  # Update last_login to the current time
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html')

# Logout Page
# Logs out the user and redirects back to the home page
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))