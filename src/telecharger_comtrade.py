"""Télécharge les données miroir UN Comtrade : ce que chaque pays déclare avoir importé de Guinée.

La Guinée ne déclare plus son commerce à l'ONU depuis plusieurs années. On utilise donc les
déclarations des pays acheteurs (données « miroir ») : importations depuis la Guinée (code 324).


Résultat : data/comtrade_miroir.csv (une ligne par année, produit et pays importateur).
"""
import csv
import json
import time
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FICHIER = RACINE / "data" / "comtrade_miroir.csv"

API = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
PAYS_REFERENCE = "https://comtradeapi.un.org/files/v1/app/reference/Reporters.json"
GUINEE = 324
ANNEES = range(2015, 2026)
PRODUITS = {
    "2606": "bauxite",          # minerais d'aluminium et leurs concentrés
    "7108": "or",               # or brut ou mi-ouvré
    "2601": "minerai de fer",
    "2818": "alumine",          # oxyde d'aluminium
}


def lire_json(url):
    """Télécharge une adresse et renvoie le JSON ; réessaie 3 fois en cas d'erreur réseau."""
    for essai in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as reponse:
                return json.load(reponse)
        except Exception as erreur:
            print(f"  erreur ({erreur}), nouvel essai dans 5 s")
            time.sleep(5)
    raise RuntimeError(f"Impossible de télécharger {url}")


def noms_des_pays():
    """Renvoie un dictionnaire code pays -> (nom, code ISO à 3 lettres)."""
    reference = lire_json(PAYS_REFERENCE)
    return {p["id"]: (p["text"], p.get("reporterCodeIsoAlpha3") or "")
            for p in reference["results"]}


def telecharger():
    pays = noms_des_pays()
    lignes = []
    for code_hs, produit in PRODUITS.items():
        for annee in ANNEES:
            url = f"{API}?partnerCode={GUINEE}&cmdCode={code_hs}&flowCode=M&period={annee}"
            donnees = lire_json(url)
            if donnees.get("error"):
                print(f"  {produit} {annee} : erreur de l'API : {donnees['error']}")
            for d in donnees.get("data") or []:
                nom, iso = pays.get(d["reporterCode"], (str(d["reporterCode"]), ""))
                lignes.append([annee, produit, code_hs, nom, iso, d["primaryValue"],
                               d["netWgt"], d["isNetWgtEstimated"]])
            print(f"{produit} {annee} : {len(donnees.get('data') or [])} pays importateurs")
            time.sleep(1.5)          # l'API publique limite le nombre d'appels par minute

    FICHIER.parent.mkdir(exist_ok=True)
    with open(FICHIER, "w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f)
        ecrivain.writerow(["annee", "produit", "code_hs", "pays_importateur", "iso3",
                           "valeur_usd", "poids_kg", "poids_estime"])
        ecrivain.writerows(lignes)
    print(f"\n{FICHIER.name} : {len(lignes)} lignes enregistrées")


if __name__ == "__main__":
    telecharger()
