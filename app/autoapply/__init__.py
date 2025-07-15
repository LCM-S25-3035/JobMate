from flask import Blueprint

bp = Blueprint('autoapply', __name__)

from app.autoapply import routes
