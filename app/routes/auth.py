from flask import (
    Blueprint, g, flash, render_template, request, redirect, url_for, session)

from ..db import query_db

from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/private')

def get_user(username):
    try:
        query = "SELECT * FROM users WHERE username = %s"
        user = query_db(query, (username,), one=True)
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        user = None

    return user

@bp.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        error = None
        user = get_user(username)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session.permanent = True
            session['user_id'] = user['id']
            flash("Authentication successful", "success")
            return redirect(url_for('auth.dashboard.dashboard'))

        flash(error, "error")
        return render_template('auth/admin.html'), 401
    
    if g.user is not None:
        return redirect(url_for('auth.dashboard.dashboard'))
    
    return render_template('auth/admin.html')

@bp.before_app_request
def load_logged_in_admin():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        try:
            query = "SELECT * FROM users WHERE id = %s"
            g.user = query_db(query, (user_id,), one=True)
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            g.user = None

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("Logout successful", "success")
    return redirect(url_for('auth.admin'))

from . import dashboard
bp.register_blueprint(dashboard.bp)
