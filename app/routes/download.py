from flask import Blueprint, send_from_directory, abort
import os

download_bp = Blueprint('download', __name__)

# Dossier par défaut où tous les fichiers à télécharger sont générés
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "generated")  # <- ou un sous-dossier type 'exports'

@download_bp.route('/download/<path:filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
    else:
        abort(404, description=f"Fichier introuvable : {filename}")
