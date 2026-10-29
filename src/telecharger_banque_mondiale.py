import json
import csv
import os
import urllib.request

PAYS = "GIN;SLE;MLI;CIV;SEN"   # Guinée, Sierra Leone, Mali, Côte d'Ivoire, Sénégal

def telecharger_indicateur(code, nom_fichier, unite):
    """Télécharge un indicateur de la Banque mondiale et l'enregistre en CSV dans data/."""
    url = (f"https://api.worldbank.org/v2/country/{PAYS}/indicator/{code}"
           f"?format=json&per_page=2000&date=2000:2026")
    with urllib.request.urlopen(url) as reponse:
        contenu = json.load(reponse)
    lignes = contenu[1]          # contenu[0] = infos sur la requête, contenu[1] = les données

    os.makedirs("data", exist_ok=True)
    with open(f"data/{nom_fichier}", "w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f)
        ecrivain.writerow(["pays", "code_pays", "annee", "valeur", "unite"])
        for l in lignes:
            ecrivain.writerow([l["country"]["value"], l["countryiso3code"], l["date"], l["value"], unite])
    print(f"{nom_fichier} : {len(lignes)} lignes enregistrées")

telecharger_indicateur("NY.GDP.MINR.RT.ZS", "rente_miniere.csv", "% du PIB")
telecharger_indicateur("TX.VAL.MMTL.ZS.UN", "export_minerais.csv", "% des exportations de marchandises")
telecharger_indicateur("NY.GDP.MKTP.CD", "pib.csv", "dollars courants")