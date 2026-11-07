"""Assistant en ligne de commande : on pose une question sur les rapports ITIE Guinée 2022-2023,
il répond en citant la page.

À lancer depuis la racine du projet : py -3.13 src/assistant_itie.py
Taper une question puis Entrée ; une ligne vide pour quitter.
"""
import pandas as pd

from rag_itie import Recherche, decouper_passages, fiches_paiements, repondre

pages = pd.read_csv("data/itie/pages_etiquetees.csv")
passages = pd.concat([
    decouper_passages(pages),
    fiches_paiements(pd.read_csv("data/itie_paiements_par_societe.csv"), pd.read_csv("data/itie_societes.csv")),
])
recherche = Recherche(passages)
print(f"{len(passages)} passages indexés (rapports ITIE 2022 et 2023).")

while True:
    question = input("\nQuestion (Entrée pour quitter) : ").strip()
    if not question:
        break
    reponse, trouves, duree = repondre(recherche, question)
    print(f"\n{reponse}")
    print(f"\n(passages utilisés : {', '.join(f'{a} p.{p}' for a, p in zip(trouves['annee'], trouves['page']))} ; {duree} s)")
