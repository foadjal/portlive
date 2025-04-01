import sqlite3
import requests
from bs4 import BeautifulSoup
import pycountry
import re
import os

# Chemin absolu vers la base de données
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(os.path.dirname(__file__), "../database/vessel_flags.db")


def init_flag_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS vessel_flags (
                imo_number TEXT PRIMARY KEY,
                flag TEXT
            )
        ''')
        conn.commit()


def convert_country_to_iso2(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        print(f"❌ LookupError: '{country_name}' non reconnu")
        return '  '


import os
import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from .utils import convert_country_to_iso2  # ou adapter si import local

# Chemin absolu vers le fichier DB


def get_vessel_flag(imo_number):
    print(f"[INFO] 📦 Recherche pavillon pour IMO {imo_number}")
    print(f"[DEBUG] Utilisation de la base: {DB_PATH}")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            # 1. Vérifie si le pavillon est déjà stocké
            c.execute('SELECT flag FROM vessel_flags WHERE imo_number = ?', (imo_number,))
            result = c.fetchone()
            if result and result[0].strip():
                print(f"[INFO] ✅ Pavillon trouvé en base : {result[0]}")
                return result[0]

            # 2. Tente une récupération en ligne
            url = f'https://www.vesselfinder.com/vessels/details/{imo_number}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }

            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                flag_cell = soup.find('td', string=re.compile(r'\bFlag\b', re.IGNORECASE))
                if flag_cell:
                    flag_value = flag_cell.find_next_sibling('td')
                    if flag_value:
                        raw_flag = flag_value.text.strip()
                        iso2 = convert_country_to_iso2(raw_flag)

                        c.execute(
                            'INSERT OR REPLACE INTO vessel_flags (imo_number, flag) VALUES (?, ?)',
                            (imo_number, iso2)
                        )
                        conn.commit()
                        print(f"[INFO] 🏴 Pavillon récupéré et enregistré : {iso2}")
                        return iso2

            except Exception as e:
                print(f"[WARN] 🌐 Erreur de récupération en ligne pour IMO {imo_number}: {e}")

            # 3. Si rien trouvé → on insère une ligne vide pour traitement manuel
            c.execute(
                'INSERT OR IGNORE INTO vessel_flags (imo_number, flag) VALUES (?, ?)',
                (imo_number, '')
            )
            conn.commit()
            print(f"[INFO] ⛔ IMO inséré pour correction manuelle : {imo_number}")
            return ''

    except Exception as e:
        print(f"[ERROR] ❌ Erreur critique avec la base de données : {e}")
        return ''




def update_flag(imo, pavillon):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE vessel_flags SET flag = ? WHERE imo_number = ?', (pavillon, imo))
        conn.commit()
