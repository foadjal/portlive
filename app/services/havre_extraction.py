# app/services/havre_extraction.py
from flask import render_template, request
import pandas as pd
import os
from datetime import datetime
from app.services.utils import (
    create_df2, afficher_donnees_dans_plage, parenthese, replace_with_first_letters,
    convert_country_codes, transcrire_type_donnees, transformer_date,
    modifier_contenu, format_excel
)

def extract_havre_data(request):
    try:
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin']

        df = create_df2("https://www.havre-port.com/fr/liste/128/arrivees-au-grand-port-maritime-du-havre",
                        '//*[@id="128"]/tbody/tr/td[4]/a', 128)
        df1 = create_df2("https://www.havre-port.com/fr/liste/129/departs-au-grand-port-maritime-du-havre",
                         '//*[@id="129"]/tbody/tr/td[5]/a', 129)
        df = df.drop_duplicates()
        df1 = df1.drop_duplicates()
        df.rename(columns={'Bateau': 'NOM'}, inplace=True)
        df1.rename(columns={'Bateau': 'NOM', 'Depart': 'Arrivée'}, inplace=True)

        df = afficher_donnees_dans_plage(df, date_debut, date_fin)
        df1 = afficher_donnees_dans_plage(df1, date_debut, date_fin)

        df = parenthese(df)
        df1 = parenthese(df1)

        df = replace_with_first_letters(df, 'Pavillon')
        df = convert_country_codes(df, 'Pavillon')
        df1 = convert_country_codes(df1, 'Pavillon')

        df['Type'] = df['Type'].apply(transcrire_type_donnees)
        df1['Type'] = df1['Type'].apply(transcrire_type_donnees)

        df = df.dropna(subset=['Type'])
        df1 = df1.dropna(subset=['Type'])

        df = transformer_date(df)
        df1 = transformer_date(df1)

        df.rename(columns={
            'Pavillon': 'NATION',
            'Provenance': 'DEPART',
            'Arrivée': 'HPA UTC',
            'Type': 'TYPE',
            'Destination': 'DESTINATION'
        }, inplace=True)
        modifier_contenu(df, 'DESTINATION', 'LE HAVRE')

        df1.rename(columns={
            'Pavillon': 'NATION',
            'Provenance': 'DEPART',
            'Arrivée': 'HPD UTC',
            'Type': 'TYPE',
            'Destination': 'DESTINATION'
        }, inplace=True)
        modifier_contenu(df1, 'DEPART', 'LE HAVRE')

        tab = ['IMO', 'NOM', 'TYPE', 'NATION', 'DEPART', 'DESTINATION', 'HPA UTC']
        tab1 = ['IMO', 'NOM', 'TYPE', 'NATION', 'DEPART', 'DESTINATION', 'HPD UTC']

        df = df[tab]
        df1 = df1[tab1]

        df['CARGAISON'] = '-'
        df1['CARGAISON'] = '-'

        maintenant = datetime.now()
        nom_fichier = maintenant.strftime("%d-%m-%y") + "extraction_havre.xlsx"

        # Dossier centralisé des fichiers
        os.makedirs("generated", exist_ok=True)
        chemin_complet = os.path.join("generated", nom_fichier)
        format_excel(df, df1, 'le havre', nom_fichier)


        fichiers = [f for f in os.listdir("generated") if f.endswith(".xlsx")]
        fichiers.sort(reverse=True)

        return render_template('test.html', nom_fichier=nom_fichier, fichiers=fichiers)

    except Exception as e:
        return render_template('error.html', error_message=str(e))