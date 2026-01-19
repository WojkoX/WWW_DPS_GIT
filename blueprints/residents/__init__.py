from flask import Blueprint

residents_bp = Blueprint(
    'residents',
    __name__,
    url_prefix='/mieszkancy'
)