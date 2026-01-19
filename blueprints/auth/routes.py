from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps
from models.user import User
from models.user import db
from blueprints.auth import auth_bp


# =====================
# DEKORATOR LOGOWANIA
# =====================
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


# =====================
# LOGOWANIE
# =====================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # jeśli już zalogowany – nie pokazuj formularza
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Podaj login i hasło', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(
            username=username,
            is_active=True
        ).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username

            flash('Zalogowano pomyślnie', 'success')
            return redirect(url_for('dashboard.dashboard'))

        flash('Nieprawidłowy login lub hasło', 'danger')

    return render_template('auth/login.html')


# =====================
# WYLOGOWANIE
# =====================
@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Wylogowano', 'info')
    return redirect(url_for('auth.login'))
