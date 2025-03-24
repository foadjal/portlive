from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.vessel_lookup import update_flag  # à créer

edit_bp = Blueprint('edit', __name__)

@edit_bp.route('/corriger_pavillons', methods=['GET', 'POST'])
def corriger_pavillons():
    if request.method == 'POST':
        imo = request.form['imo']
        pavillon = request.form['pavillon']
        update_flag(imo, pavillon)
        flash(f"Pavillon mis à jour pour IMO {imo} → {pavillon}")
        return redirect(url_for('edit.corriger_pavillons'))

    # charger les lignes manquantes depuis la base
    import sqlite3
    conn = sqlite3.connect('vessel_flags.db')
    c = conn.cursor()
    c.execute("SELECT * FROM vessel_flags WHERE flag = '  '")
    lignes_vides = c.fetchall()
    conn.close()

    return render_template('corriger_pavillons.html', pavillons_vides=lignes_vides)
