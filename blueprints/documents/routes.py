import zipfile
from flask import send_file, redirect, url_for, session
from functools import wraps
from services.docx_generator import generate_all
from blueprints.documents import documents_bp


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@documents_bp.route('/generuj')
@login_required
def generate_docs():
    paths = generate_all()

    zip_path = 'generated/DPS_diety.zip'
    with zipfile.ZipFile(zip_path, 'w') as z:
        for p in paths:
            z.write(p, arcname=p.split('/')[-1])

    return send_file(zip_path, as_attachment=True)
