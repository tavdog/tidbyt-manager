import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import generate_password_hash
import tidbyt_manager.db as db
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        #db = get_db()
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        if error != None and db.get_user(username):
            error = 'User {} is already registered.'.format(username)    
        if error is None:
            user = dict()
            user["username"] = username
            user["password"] = password
            db.create_user_dir(username)
            db.save_user(user)
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #db = get_db()
        error = None
        user = db.auth_user(username,password)
        if user is False:
            error = 'Incorrect username/password.'
        if error is None:
            session.clear()
            print("username" + username)
            session['username'] = username
            return redirect(url_for('index'))
        flash(error)
    
    return render_template('auth/login.html')

# edit user info, namely password
@bp.route('/edit', methods=('GET', 'POST'))
def edit():
    if request.method == 'POST':
        username = session['username']
        old_pass = request.form['old_password']
        password = generate_password_hash(request.form['password'])
        error = None
        user = db.auth_user(username,old_pass)
        if user is False:
            error = 'Bad old password.'
        if error is None:
            user['password'] = password
            db.save_user(user)
            flash("Success")
            return redirect(url_for('index'))
        flash(error)
    
    return render_template('auth/edit.html')

@bp.before_app_request
def load_logged_in_user():
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        if db.user_exists(username):
            g.user = db.get_user(username)
        else:
            g.user = None

@bp.route('/logout')
def logout():
    session.clear()
    flash("Logged Out")
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view