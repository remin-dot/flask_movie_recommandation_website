"""Language selection routes."""

from flask import Blueprint, redirect, request, session, url_for
from app.i18n import SUPPORTED_LANGUAGES


locale_bp = Blueprint('locale', __name__)


@locale_bp.route('/lang/<lang_code>')
def set_language(lang_code):
    if lang_code in SUPPORTED_LANGUAGES:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('movie.home'))
