# app/routes/havre.py
from flask import Blueprint, render_template, request
from app.services.havre_extraction import extract_havre_data

havre_bp = Blueprint('havre', __name__, url_prefix='/havre_port')

@havre_bp.route('/', methods=['GET', 'POST'])
def havre_port():
    if request.method == 'POST':
        return extract_havre_data(request)
    return render_template('havre_port.html')
