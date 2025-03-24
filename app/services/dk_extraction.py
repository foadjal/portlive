# app/services/dk_extraction.py
from flask import render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd
import os

from app.services.utils import (
    get_element_html, find_div_with_viewbox, extract_info_from_divs,
    supprimer_D, convertion, transformer_date,
    supprimer_doublons, transcrire_type, modifier_contenu, format_excel
)
from app.services.vessel_lookup import get_vessel_flag

def extract_dunkerque_data(request):
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    username_xpath = '//*[@id="Contenu_tbxUser"]'
    password_xpath = '//*[@id="Contenu_tbxUserKey"]'
    url = 'https://sirene.dunkerque-port.fr/Application/Login.aspx'

    driver.get(url)
    connexion_reussie = False

    while not connexion_reussie:
        username = request.form['nom_utilisateur']
        password = request.form['mot_de_passe']

        username_field = driver.find_element(By.XPATH, username_xpath)
        password_field = driver.find_element(By.XPATH, password_xpath)

        username_field.clear()
        password_field.clear()
        username_field.send_keys(username)
        password_field.send_keys(password)

        driver.find_element(By.XPATH, '//*[@id="Contenu_bpValide"]').click()
        driver.implicitly_wait(2)

        try:
            driver.find_element(By.XPATH, '/html/body/form/div[3]/nav/ul/li[1]/ul/li[2]/a/span')
            connexion_reussie = True
        except:
            e = "Identifiant ou mot de passe incorrect. Veuillez réessayer."
            driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/button/span[1]').click()
            return render_template('error.html', error_message=e)

    try:
        xpath_navire_data = '//*[@id="ContenuTimer_UpdatePnlAttendu"]'
        navire_html = get_element_html(driver, xpath_navire_data)
        divs = find_div_with_viewbox(navire_html)
        df = extract_info_from_divs(divs)
        df = supprimer_D(df).rename(columns={'Date et Heure': 'Arrivée'})
        df = convertion(df)
        df = transformer_date(df)

        df.rename(columns={
            'Nom Navire': 'NOM',
            'Pavillon': 'NATION',
            'Lloyd': 'IMO',
            'Type Navire': 'TYPE',
            'Destination': 'DESTINATION'
        }, inplace=True)

        if 'NATION' not in df.columns:
            df['NATION'] = '  '

        df = enrichir_pavillons(df)
        df = supprimer_doublons(df)
        df['TYPE'] = df['TYPE'].apply(transcrire_type)
        df = df.dropna(subset=['TYPE'])
        df['NOM'] = df['NOM'].str.replace(r"\((.*?)\)", r"\1", regex=True)
        df['CARGAISON'] = '-'
        df['DESTINATION'] = '-'

        df_attendu = df[df['Mouvement'] == 'E'].copy()
        df_depart = df[df['Mouvement'] == 'S'].copy()

        tab = ['IMO', 'NOM', 'TYPE', 'NATION', 'Provenance ou Destination', 'DESTINATION', 'Arrivée', 'CARGAISON']
        df_attendu = df_attendu[tab].copy()
        df_depart = df_depart[tab].copy()

        modifier_contenu(df_attendu, 'DESTINATION', 'DUNKERQUE')
        modifier_contenu(df_depart, 'DESTINATION', 'DUNKERQUE')

        df_attendu.rename(columns={
            'Provenance ou Destination': 'DEPART',
            'Arrivée': 'HPA UTC',
            'NATION': 'Pavillon'
        }, inplace=True)

        df_depart.rename(columns={
            'Provenance ou Destination': 'DESTINATION',
            'Arrivée': 'HPD UTC',
            'DESTINATION': 'DEPART',
            'NATION': 'Pavillon'
        }, inplace=True)

        os.makedirs("generated", exist_ok=True)
        maintenant = datetime.now()
        nom_fichier = maintenant.strftime("%d-%m-%y") + "extraction_dunkerque.xlsx"
        format_excel(df_attendu, df_depart, 'dunkerque', nom_fichier)

        fichiers = [f for f in os.listdir("generated") if f.endswith(".xlsx")]
        fichiers.sort(reverse=True)

        return render_template('test.html', nom_fichier=nom_fichier, fichiers=fichiers)

    except Exception as e:
        return render_template('error.html', error_message=str(e))

def enrichir_pavillons(df):
    df['NATION'] = df.get('NATION', '  ')
    df_missing = df[df['NATION'].isin(['', '  ']) & df['IMO'].notna()]
    unique_imos = df_missing['IMO'].dropna().unique()
    pavillons = [(imo, get_vessel_flag(str(int(imo)))) for imo in unique_imos]
    df_flags = pd.DataFrame(pavillons, columns=['IMO', 'NATION'])
    df.drop(columns=['NATION'], inplace=True, errors='ignore')
    df = df.merge(df_flags, on='IMO', how='left')
    return df
