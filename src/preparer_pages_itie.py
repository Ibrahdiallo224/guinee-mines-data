"""Prépare les données d'entraînement : une ligne par page des rapports ITIE 2022 et 2023, avec son thème.

À lancer depuis la racine du projet : py -3.13 src/preparer_pages_itie.py
Résultat : data/itie/pages_etiquetees.csv (dans data/itie/, donc pas envoyé sur GitHub, comme les PDF).
"""
import pandas as pd

from pages_itie import pages_etiquetees

themes = pd.read_csv("data/itie_themes.csv", dtype=str)       # dtype=str : « 4.10 » doit rester « 4.10 », pas 4.1
themes = dict(zip(themes["section"], themes["theme"]))         # {"1": "synthese", "4.1": "secteur_minier", ...}

tableaux = []
for annee in (2022, 2023):
    print(f"Lecture du rapport {annee} (quelques minutes : pdfplumber lit les 400 pages)...")
    pages = pages_etiquetees(f"data/itie/rapport_itie_{annee}.pdf", annee, themes)
    print(pages.groupby("theme").size().to_string(), "\n")
    tableaux.append(pages)

pd.concat(tableaux).to_csv("data/itie/pages_etiquetees.csv", index=False)
print("data/itie/pages_etiquetees.csv écrit")
