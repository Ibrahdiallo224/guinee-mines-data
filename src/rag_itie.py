"""Assistant qui répond aux questions sur les rapports ITIE Guinée 2022 et 2023, en citant ses sources (RAG).

RAG = Retrieval-Augmented Generation, en deux temps :
1. Recherche : on découpe les rapports en passages et on cherche, avec TF-IDF, les passages
   les plus proches de la question (le même principe que le classifieur de l'étape 7b).
2. Génération : on envoie à Gemini la question et SEULEMENT ces passages. Il doit répondre
   à partir des extraits, citer la page, et dire « je ne sais pas » si la réponse n'y est pas.
"""
import os
import re
import time

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

MODELE = "gemini-3.5-flash"
TAILLE_PASSAGE = 1200          # caractères : assez pour un paragraphe ou quelques lignes de tableau
CONSIGNE = (
    "Tu réponds à des questions sur les rapports ITIE (Initiative pour la transparence dans les industries "
    "extractives) de la Guinée. Utilise UNIQUEMENT les extraits fournis. Recopie les chiffres exactement comme "
    "dans l'extrait, avec leur unité (GNF, %, etc.). Termine par la source au format (rapport ANNEE, page N). "
    "Si la réponse n'est pas dans les extraits, réponds seulement : « Je ne sais pas »."
)


def decouper_passages(pages, taille=TAILLE_PASSAGE):
    """Coupe le texte de chaque page en passages d'environ `taille` caractères, sans couper une ligne en deux.

    Une page entière mélange souvent plusieurs sujets : des passages plus courts rendent la recherche plus précise.
    """
    lignes_passages = []
    for page in pages.itertuples():
        morceau = ""
        for ligne in page.texte.split("\n"):
            if len(morceau) + len(ligne) > taille and morceau:
                lignes_passages.append((page.annee, page.page, page.section, morceau.strip()))
                morceau = ""
            morceau += ligne + "\n"
        if morceau.strip():
            lignes_passages.append((page.annee, page.page, page.section, morceau.strip()))
    return pd.DataFrame(lignes_passages, columns=["annee", "page", "section", "passage"])


PAGES_TABLEAU = {2022: 156, 2023: 151}   # page du tableau « Rapprochement des flux de paiement par société »


def montant(n):
    """3291879786828 -> « 3 291 879 786 828 », comme dans le rapport."""
    return f"{int(n):,}".replace(",", " ")


def fiches_paiements(paiements, societes):
    """Une phrase par société et par année, écrite à partir du tableau extrait à l'étape 7.

    Dans le PDF, une ligne de tableau n'est qu'une suite de chiffres : la recherche la retrouve mal.
    Réécrite en phrase, avec le sigle de la société (SMB, CBG…), elle devient facile à retrouver.
    """
    noms_courts = dict(zip(societes["nom_itie"], societes["nom_court"]))
    fiches = []
    for ligne in paiements.itertuples():
        court = noms_courts.get(ligne.nom, "")
        texte = (
            f"Rapport ITIE {ligne.annee}, tableau de rapprochement des paiements par société. "
            f"Société : {ligne.nom} ({court}). "
            f"Montant que la société déclare avoir payé à l'État : {montant(ligne.societe_initial)} GNF. "
            f"Montant que l'État (gouvernement) déclare avoir reçu de la société : {montant(ligne.etat_initial)} GNF. "
            f"Écart entre la société et l'État : {montant(ligne.societe_initial - ligne.etat_initial)} GNF. "
            f"Après ajustements : la société déclare {montant(ligne.societe_ajuste)} GNF, "
            f"l'État déclare {montant(ligne.etat_ajuste)} GNF."
        )
        fiches.append((ligne.annee, PAGES_TABLEAU[ligne.annee], "tableau", texte))
    return pd.DataFrame(fiches, columns=["annee", "page", "section", "passage"])


class Recherche:
    """Index TF-IDF des passages : retrouve les passages les plus proches d'une question."""

    def __init__(self, passages):
        self.passages = passages.reset_index(drop=True)
        self.tfidf = TfidfVectorizer(
            strip_accents="unicode",                      # « société » = « societe »
            token_pattern=r"(?u)\b[^\W\d_]{2,}\b",        # des mots d'au moins 2 lettres : les sigles (SMB, CBG) comptent, les chiffres non
            sublinear_tf=True,
        )
        self.matrice = self.tfidf.fit_transform(self.passages["passage"])

    def chercher(self, question, nb=4, annee=None):
        """Les nb passages les plus proches de la question, avec leur score de similarité (0 à 1).

        Si la question cite une année (2022 ou 2023), on ne cherche que dans le rapport de cette année.
        """
        if annee is None:
            trouvee = re.search(r"\b(2022|2023)\b", question)
            annee = int(trouvee.group(1)) if trouvee else None
        # les vecteurs TF-IDF sont de longueur 1 : le produit scalaire donne directement la similarité cosinus
        scores = (self.matrice @ self.tfidf.transform([question]).T).toarray().ravel()
        resultat = self.passages.assign(score=scores.round(3))
        if annee is not None:
            resultat = resultat[resultat["annee"] == annee]
        return resultat.sort_values("score", ascending=False).head(nb)


def construire_message(question, passages):
    """Le texte envoyé à Gemini : les extraits numérotés avec leur source, puis la question."""
    extraits = "\n\n".join(
        f"[Extrait {i} : rapport {p.annee}, page {p.page}]\n{p.passage}"
        for i, p in enumerate(passages.itertuples(), start=1)
    )
    return f"{extraits}\n\nQuestion : {question}"


def demander_gemini(message):
    """Envoie le message à Gemini avec la consigne ; renvoie sa réponse et sa durée en secondes."""
    from dotenv import load_dotenv
    from google import genai
    from google.genai import types

    load_dotenv()                                         # la clé est lue dans .env, jamais affichée
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for essai in range(5):
        try:
            debut = time.time()
            reponse = client.models.generate_content(
                model=MODELE,
                contents=message,
                config=types.GenerateContentConfig(system_instruction=CONSIGNE, temperature=0),
            )
            return reponse.text.strip(), round(time.time() - debut, 1)
        except Exception as erreur:
            if "429" in str(erreur) and "PerDay" in str(erreur):
                raise RuntimeError(f"Quota quotidien de {MODELE} atteint : relancer demain") from erreur
            if "429" in str(erreur) or "503" in str(erreur):
                print(f"  Gemini indisponible ({str(erreur)[:3]}), pause d'une minute...")
                time.sleep(60)
            else:
                raise
    raise RuntimeError("Gemini ne répond plus après 5 essais")


def repondre(recherche, question, nb=4):
    """La chaîne complète : recherche des passages, puis réponse de Gemini. Renvoie (réponse, passages, durée)."""
    passages = recherche.chercher(question, nb=nb)
    reponse, duree = demander_gemini(construire_message(question, passages))
    return reponse, passages, duree


def sans_espaces(texte):
    """« 3 291 879 » -> « 3291879 » : pour comparer des chiffres écrits avec des espaces différents."""
    return re.sub(r"\s", "", str(texte)).lower()


def reponse_juste(reponse, attendue):
    """Vrai si la réponse attendue (chiffre ou « je ne sais pas ») se trouve dans la réponse."""
    return sans_espaces(attendue) in sans_espaces(reponse)
