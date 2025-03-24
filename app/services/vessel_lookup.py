import sqlite3
import requests
from bs4 import BeautifulSoup
import pycountry
import re

def init_flag_db():
    conn = sqlite3.connect('vessel_flags.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS vessel_flags (
            imo_number TEXT PRIMARY KEY,
            flag TEXT
        )
    ''')
    conn.commit()
    conn.close()

def convert_country_to_iso2(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        print(f"❌ LookupError: '{country_name}' non reconnu")
        return '  '

def get_vessel_flag(imo_number):
    conn = sqlite3.connect('vessel_flags.db')
    c = conn.cursor()
    c.execute('SELECT flag FROM vessel_flags WHERE imo_number = ?', (imo_number,))
    result = c.fetchone()
    if result:
        conn.close()
        return result[0]

    url = f'https://www.vesselfinder.com/vessels/details/{imo_number}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Repérage intelligent du pavillon
        flag_cell = soup.find('td', string=re.compile(r'\bFlag\b', re.IGNORECASE))
        if flag_cell:
            flag_value = flag_cell.find_next_sibling('td')
            if flag_value:
                raw_flag = flag_value.text.strip()
                iso2 = convert_country_to_iso2(raw_flag)
                c.execute('INSERT INTO vessel_flags (imo_number, flag) VALUES (?, ?)', (imo_number, iso2))
                conn.commit()
                conn.close()
                return iso2

    except Exception as e:
        print('error:', e)
    conn.close()
    return '  '


def update_flag(imo, pavillon):
    conn = sqlite3.connect('vessel_flags.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE vessel_flags SET flag = ? WHERE imo_number = ?', (pavillon, imo))
    conn.commit()
    conn.close()
