from flask import Blueprint

forms_bp = Blueprint('forms', __name__)

from . import routes
