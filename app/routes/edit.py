from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.vessel_lookup import update_flag  # à créer
import sqlite3
import os

edit_bp = Blueprint('edit', __name__)

# Récupérer le chemin absolu vers la base de données
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'database', 'vessel_flags.db')

@edit_bp.route('/corriger_pavillons', methods=['GET', 'POST'])
def corriger_pavillons():
    if request.method == 'POST':
        imo = request.form['imo']
        pavillon = request.form['pavillon']
        update_flag(imo, pavillon)
        flash(f"Pavillon mis à jour pour IMO {imo} → {pavillon}")
        return redirect(url_for('edit.corriger_pavillons'))

    # Charger les lignes manquantes depuis la base
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM vessel_flags WHERE flag = '  '")
        lignes_vides = c.fetchall()

    return render_template('corriger_pavillons.html', pavillons_vides=lignes_vides)