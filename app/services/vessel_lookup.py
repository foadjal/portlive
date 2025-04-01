import sqlite3
import requests
from bs4 import BeautifulSoup
import pycountry
import re
import os

# Chemin absolu vers la base de données
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'database', 'vessel_flags.db')


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


def get_vessel_flag(imo_number):
    # Vérifie d'abord si le pavillon est déjà stocké
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT flag FROM vessel_flags WHERE imo_number = ?', (imo_number,))
        result = c.fetchone()
        if result:
            return result[0]

        # Sinon on va le chercher en ligne
        url = f'https://www.vesselfinder.com/vessels/details/{imo_number}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
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

                    # On stocke le résultat
                    c.execute('INSERT INTO vessel_flags (imo_number, flag) VALUES (?, ?)', (imo_number, iso2))
                    conn.commit()
                    return iso2

        except Exception as e:
            print(f"🌐 Erreur de récupération pour IMO {imo_number}: {e}")

        # On insère quand même l'IMO avec un flag vide pour correction manuelle
        c.execute('INSERT INTO vessel_flags (imo_number, flag) VALUES (?, ?)', (imo_number, ' '))
        conn.commit()
        return ' '



def update_flag(imo, pavillon):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE vessel_flags SET flag = ? WHERE imo_number = ?', (pavillon, imo))
        conn.commit()
