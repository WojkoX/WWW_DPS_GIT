from flask import Blueprint

diets_bp = Blueprint(
    'diets',
    __name__,
    url_prefix='/diety'
)