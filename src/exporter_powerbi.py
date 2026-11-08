"""Préparation des tables du tableau de bord Power BI : un fichier CSV par table, dans powerbi/donnees/.

À lancer depuis la racine du projet : py -3.13 src/exporter_powerbi.py
Réutilisation des requêtes SQL et de la prévision de l'étape 5 : mêmes chiffres que dans les notebooks.
"""
import pandas as pd

from prevision import prevoir
from requetes import RACINE, requete

SORTIE = RACINE / "powerbi" / "donnees"
SORTIE.mkdir(parents=True, exist_ok=True)


def enregistrer(tableau, nom):
    """Écrit le CSV avec des virgules comme séparateur et le point comme décimale (lu tel quel par Power BI)."""
    tableau.round(3).to_csv(SORTIE / f"{nom}.csv", index=False, encoding="utf-8")
    print(f"{nom}.csv : {len(tableau)} lignes")


# 1. Bauxite : production observée (2000-2024) et prévision jusqu'en 2035, avec son intervalle à 95 %
observe = requete("05_bauxite_serie").df()
prevision, _ = prevoir(observe, debut=2016, fin=2024, horizon=2035)       # le même modèle qu'à l'étape 5 (droite 2016-2024)
bauxite = pd.concat([
    observe.rename(columns={"valeur": "production_mt"}).assign(type="observé"),
    prevision.rename(columns={"prevision": "production_mt", "bas": "bas_mt", "haut": "haut_mt"}).assign(type="prévision"),
])
enregistrer(bauxite, "bauxite_production")

# 2. Autres tables : une requête SQL chacune
enregistrer(requete("09_pbi_bauxite_monde").df(), "bauxite_monde")
enregistrer(requete("09_pbi_exportations_entreprises").df(), "exportations_entreprises")
enregistrer(requete("09_pbi_clients").df(), "clients")
enregistrer(requete("09_pbi_paiements_itie").df(), "paiements_itie")
enregistrer(requete("04_scenarios_exportations").df(), "simandou_scenarios")

# 3. Table des années, reliée à toutes les autres dans Power BI : un seul filtre « année » agit partout
enregistrer(pd.DataFrame({"annee": range(2000, 2036)}), "annees")
