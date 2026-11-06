"""Demande à Gemini (Google) le thème de chaque page du rapport ITIE 2023, pour le comparer à mon modèle.

À lancer depuis la racine du projet : py -3.13 src/gemini_pages.py
Il faut une clé dans le fichier .env : GEMINI_API_KEY=...
Résultat : data/gemini_pages_2023.csv (page, thème donné par Gemini, durée de la réponse).

L'offre gratuite limite le nombre d'appels par minute et par jour : le script attend entre deux pages,
et il reprend là où il s'était arrêté si on le relance. Avec gemini-3.5-flash, le quota du jour
s'épuise après une vingtaine de pages : la comparaison (notebook 07c) porte sur les pages obtenues.
"""
import os
import time

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

MODELE = "gemini-3.5-flash"     # si Google le retire, le message d'erreur donnera la liste des modèles disponibles
PAUSE = 7                       # secondes entre deux pages, pour rester sous la limite gratuite
SORTIE = "data/gemini_pages_2023.csv"

load_dotenv()                                                   # lit .env et met la clé dans les variables d'environnement
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# La consigne : les mêmes 7 thèmes que le modèle TF-IDF, avec ce que chacun contient
themes = pd.read_csv("data/itie_themes.csv", dtype=str)
definitions = themes.groupby("theme")["contenu"].apply("; ".join)
CONSIGNE = ("Tu reçois le texte d'une page d'un rapport ITIE (Initiative pour la transparence dans les industries "
            "extractives) de la Guinée. Réponds uniquement par le thème de la page, parmi :\n"
            + "\n".join(f"- {theme} : {contenu}" for theme, contenu in definitions.items()))


def demander_theme(texte):
    """Envoie une page à Gemini et renvoie le thème qu'il choisit."""
    for essai in range(10):
        try:
            reponse = client.models.generate_content(
                model=MODELE,
                contents=texte[:6000],                          # une page dépasse rarement 6000 caractères
                config=types.GenerateContentConfig(
                    system_instruction=CONSIGNE,
                    temperature=0,                              # toujours la même réponse pour la même page
                    response_mime_type="text/x.enum",           # Gemini doit répondre par un des thèmes, rien d'autre
                    response_schema={"type": "STRING", "enum": list(definitions.index)},
                ),
            )
            return reponse.text.strip()
        except Exception as erreur:
            if "429" in str(erreur) and "PerDay" in str(erreur):
                # quota du jour épuisé : inutile d'attendre une minute, il faut attendre le lendemain
                raise RuntimeError(f"Quota quotidien de {MODELE} atteint : relancer le script demain, il reprendra où il en était")
            if "429" in str(erreur) or "503" in str(erreur):
                # 429 = trop d'appels de ma part ; 503 = serveurs de Google surchargés.
                # Dans les deux cas c'est temporaire : on attend une minute et on réessaie.
                print(f"  Gemini indisponible ({str(erreur)[:3]}), pause d'une minute (essai {essai + 1}/10)...")
                time.sleep(60)
            elif "404" in str(erreur):                          # 404 = modèle inconnu : on affiche ceux qui existent
                print("Modèle introuvable. Modèles disponibles :")
                for m in client.models.list():
                    print("  ", m.name)
                raise
            else:
                raise
    raise RuntimeError("Gemini ne répond plus après 10 essais : relancer le script plus tard, il reprendra où il en était")


pages = pd.read_csv("data/itie/pages_etiquetees.csv")
pages = pages[pages["annee"] == 2023]

# Reprise : on garde les pages déjà traitées lors d'un lancement précédent
deja_faites = pd.read_csv(SORTIE) if os.path.exists(SORTIE) else pd.DataFrame(columns=["page", "theme_gemini", "secondes"])
a_faire = pages[~pages["page"].isin(deja_faites["page"])]
print(f"{len(deja_faites)} pages déjà faites, {len(a_faire)} à demander à {MODELE}")

resultats = deja_faites.to_dict("records")
for numero, (page, texte) in enumerate(zip(a_faire["page"], a_faire["texte"]), start=1):
    debut = time.time()
    theme = demander_theme(texte)
    resultats.append({"page": page, "theme_gemini": theme, "secondes": round(time.time() - debut, 2)})
    print(f"{numero}/{len(a_faire)}  page {page} : {theme}")
    pd.DataFrame(resultats).to_csv(SORTIE, index=False)        # on enregistre à chaque page : rien n'est perdu si ça coupe
    time.sleep(PAUSE)

print(f"\n{SORTIE} : {len(resultats)} pages")
