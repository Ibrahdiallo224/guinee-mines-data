"""Extrait des rapports ITIE le tableau des paiements par société et l'enregistre dans data/."""
import pandas as pd

from itie import trouver_page, paiements_par_societe, verifier_total

TITRE = "Rapprochement des flux de paiement en numéraire par société extractive"

tableaux = []
for annee in (2022, 2023):
    chemin = f"data/itie/rapport_itie_{annee}.pdf"
    page = trouver_page(chemin, TITRE)
    print(f"\n{annee} : tableau trouvé page {page}")
    tableau = paiements_par_societe(chemin, page, annee)
    verifier_total(tableau)                                     # la somme des sociétés = le total du rapport ?
    tableaux.append(tableau[tableau["nom"] != "Total"])          # on garde les sociétés, le total se recalcule

resultat = pd.concat(tableaux)
resultat.to_csv("data/itie_paiements_par_societe.csv", index=False)
print(f"\ndata/itie_paiements_par_societe.csv : {len(resultat)} lignes")
