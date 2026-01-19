from flask import Blueprint

import_csv_bp = Blueprint(
    'import_csv',
    __name__,
    url_prefix='/import'
)