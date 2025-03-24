# app/routes/dk.py
from flask import Blueprint, render_template, request
from app.services.dk_extraction import extract_dunkerque_data

dk_bp = Blueprint('dk', __name__)

@dk_bp.route('/', methods=['GET', 'POST'])
def dk_port():
    if request.method == 'POST':
        return extract_dunkerque_data(request)
    return render_template('dk_port.html')
