from functools import wraps
from flask import flash, redirect, url_for, session

def login_required(f):
    @wraps(f)
    def decorated_function(*k, **ka):
        if 'user_id' not in session:
            flash('you need to login before accessing this','warning')
            return redirect(url_for('auth.login'))
        return f(*k,**ka)

    return decorated_function