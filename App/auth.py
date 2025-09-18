from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .database import get_db, engine,init_db
from .user_model import Base, User
from sqlalchemy.exc import IntegrityError

authbp = Blueprint('auth', __name__, url_prefix='/auth')

@authbp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('username and password needed please !!', 'warning')
            return render_template('register.html')
        
        # The code below will only run if a username and password are provided
        with get_db() as db_session:
            try:
                newuser = User(username=username)
                newuser.set_hashpassword(password)
                db_session.add(newuser)
                db_session.commit()
                flash('you  heave been registed successfully, please login!!', 'success')
                return redirect(url_for('auth.login'))
            except IntegrityError:
                db_session.rollback()
                flash('user already exists please login instead or choose a different one', 'danger')
            except Exception as e:
                flash(f'unexpected error occurred: {e}', 'danger')
    return render_template('register.html')
@authbp.route('/login', methods = ['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        with get_db() as db_session:
            user = db_session.query(User).filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id']= user.id
                session['username']=username
                flash(f'Logged in successfully as {username}', 'success')
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('invalid name or username!! check and try again','danger')
                return render_template('login.html')
    return render_template('login.html')
@authbp.route('/logout')
def logout():
    session.pop('user_id',None)
    session.pop('username',None)
    flash('you have been logged out !! login again','info')
    return redirect(url_for('auth.login'))
