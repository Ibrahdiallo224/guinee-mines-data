"""Page web de l'assistant ITIE Guinée (Streamlit) : on pose une question, il répond en citant la page du rapport.

À lancer depuis la racine du projet : py -3.13 -m streamlit run src/app_assistant.py
La page s'ouvre dans le navigateur (http://localhost:8501). Ctrl+C dans le terminal pour l'arrêter.
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).parent))
from rag_itie import Recherche, decouper_passages, fiches_paiements, repondre  # noqa: E402

RACINE = Path(__file__).parent.parent
EXEMPLES = [
    "Combien la SMB a-t-elle déclaré avoir payé à l'État en 2023 ?",
    "Combien de sociétés minières sont dans le périmètre de réconciliation en 2023 ?",
    "De combien les revenus du secteur extractif ont-ils baissé en 2023 ?",
    "Quel taux de change USD/GNF est utilisé dans le rapport 2022 ?",
]

st.set_page_config(page_title="Assistant ITIE Guinée", page_icon="⛏️", layout="centered")


@st.cache_resource          # l'index n'est construit qu'une fois, pas à chaque question
def charger_recherche():
    pages = pd.read_csv(RACINE / "data/itie/pages_etiquetees.csv")
    passages = pd.concat([
        decouper_passages(pages),
        fiches_paiements(pd.read_csv(RACINE / "data/itie_paiements_par_societe.csv"),
                         pd.read_csv(RACINE / "data/itie_societes.csv")),
    ])
    return Recherche(passages)


recherche = charger_recherche()

# ---------- Colonne de gauche : présentation ----------
with st.sidebar:
    st.header("Comment ça marche")
    st.markdown(
        f"""
1. **Recherche** : la question est comparée aux **{len(recherche.passages)} passages** des rapports
   ITIE Guinée 2022 et 2023 (TF-IDF). Les plus proches sont retenus.
2. **Réponse** : Gemini reçoit la question et **seulement ces passages**. Il doit citer la page
   et répondre « Je ne sais pas » si l'information n'y est pas.

Test sur 10 questions à réponse connue : **10 bonnes réponses sur 10**.
"""
    )
    nb_passages = st.slider("Nombre de passages envoyés à Gemini", 2, 8, 4)
    st.caption("Projet Guinée Mines Data · rapports ITIE (eiti.org)")

# ---------- Page principale ----------
st.title("⛏️ Assistant ITIE Guinée")
st.write("Posez une question sur les paiements des sociétés minières à l'État guinéen (rapports ITIE 2022 et 2023).")

if "historique" not in st.session_state:
    st.session_state.historique = []        # liste de (question, réponse, passages)

st.write("**Exemples :**")
colonnes = st.columns(2)
question_exemple = None
for i, exemple in enumerate(EXEMPLES):
    if colonnes[i % 2].button(exemple, use_container_width=True):
        question_exemple = exemple


def afficher(question, reponse, passages):
    """Une question, sa réponse, et les passages utilisés (repliés)."""
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        st.write(reponse)
        with st.expander("Passages utilisés"):
            for p in passages.itertuples():
                st.markdown(f"**Rapport {p.annee}, page {p.page}** · similarité {p.score:.2f}")
                st.text(p.passage[:800])


for ancienne in st.session_state.historique:
    afficher(*ancienne)

question = st.chat_input("Votre question") or question_exemple
if question:
    try:
        with st.spinner("Recherche dans les rapports, puis rédaction de la réponse…"):
            reponse, passages, duree = repondre(recherche, question, nb=nb_passages)
        st.session_state.historique.append((question, reponse, passages))
        afficher(question, reponse, passages)
        st.caption(f"Réponse en {duree} s")
    except RuntimeError as erreur:          # quota Gemini épuisé, par exemple
        st.error(str(erreur))
