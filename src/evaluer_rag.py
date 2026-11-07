"""Pose à l'assistant RAG les questions de test (data/rag_questions.csv) et enregistre ses réponses.

À lancer depuis la racine du projet : py -3.13 src/evaluer_rag.py
Une question = un seul appel à Gemini (10 questions : environ 2 minutes).
Résultat : data/rag_reponses.csv, analysé dans le notebook 08.
"""
import os
import time

import pandas as pd

from rag_itie import Recherche, decouper_passages, fiches_paiements, repondre, reponse_juste

SORTIE = "data/rag_reponses.csv"
PAUSE = 7                      # secondes entre deux questions, pour rester sous la limite gratuite

pages = pd.read_csv("data/itie/pages_etiquetees.csv")
passages = pd.concat([
    decouper_passages(pages),
    fiches_paiements(pd.read_csv("data/itie_paiements_par_societe.csv"), pd.read_csv("data/itie_societes.csv")),
])
recherche = Recherche(passages)
questions = pd.read_csv("data/rag_questions.csv", dtype=str).fillna("")

# Reprise : les questions déjà posées lors d'un lancement précédent ne sont pas reposées
deja_faites = pd.read_csv(SORTIE, dtype=str) if os.path.exists(SORTIE) else pd.DataFrame(columns=["question"])
resultats = deja_faites.to_dict("records")

for ligne in questions[~questions["question"].isin(deja_faites["question"])].itertuples():
    reponse, trouves, duree = repondre(recherche, ligne.question)
    resultats.append({
        "question": ligne.question,
        "reponse_attendue": ligne.reponse_attendue,
        "reponse_gemini": reponse,
        "pages_trouvees": ", ".join(f"{a}-p{p}" for a, p in zip(trouves["annee"], trouves["page"])),
        "juste": reponse_juste(reponse, ligne.reponse_attendue),
        "secondes": duree,
    })
    print(f"{'OK  ' if resultats[-1]['juste'] else 'FAUX'} {ligne.question}\n     -> {reponse}\n")
    pd.DataFrame(resultats).to_csv(SORTIE, index=False)        # enregistré à chaque question
    time.sleep(PAUSE)

print(f"{SORTIE} : {len(resultats)} questions")
