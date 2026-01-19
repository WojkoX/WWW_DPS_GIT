from flask import Blueprint

file_explorer_bp = Blueprint(
    'fileexplorer',
    __name__,
    url_prefix='/csvupload',
    template_folder='templates',
    static_folder='static'
)

from .file_explorer import *
