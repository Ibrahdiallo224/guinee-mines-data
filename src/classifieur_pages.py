"""Modèle d'IA entraîné sur les rapports ITIE : il lit le texte d'une page de rapport ITIE et dit de quel thème elle parle.

Deux étapes, enchaînées dans un « pipeline » scikit-learn :
1. TF-IDF : transforme chaque page en une liste de nombres, un par mot du vocabulaire.
   Un mot compte beaucoup s'il est fréquent dans la page mais rare dans les autres pages.
2. Régression logistique : apprend, pour chaque thème, quels mots le rendent probable.
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline


def creer_modele(classifieur=None):
    """Le modèle, pas encore entraîné. Par défaut, une régression logistique ; on peut en passer un autre."""
    if classifieur is None:
        classifieur = LogisticRegression(max_iter=2000, class_weight="balanced")   # balanced : les petits thèmes comptent autant
    return make_pipeline(
        TfidfVectorizer(
            strip_accents="unicode",                  # « société » et « societe » deviennent le même mot
            token_pattern=r"(?u)\b[^\W\d_]{3,}\b",    # un mot = 3 lettres ou plus, sans chiffres
            ngram_range=(1, 2),                       # on garde aussi les paires de mots : « taxe miniere »
            min_df=2,                                 # un mot vu dans une seule page ne sert à rien
            max_df=0.7,                               # un mot présent dans plus de 70 % des pages non plus
            sublinear_tf=True,                        # 10 fois le même mot ne compte pas 10 fois plus
        ),
        classifieur,
    )


def mots_les_plus_utiles(modele, nb=8):
    """Pour chaque thème, les mots qui font le plus monter sa probabilité."""
    tfidf, regression = modele.named_steps.values()
    vocabulaire = tfidf.get_feature_names_out()
    lignes = {}
    for theme, poids in zip(regression.classes_, regression.coef_):
        meilleurs = poids.argsort()[::-1][:nb]                 # indices des plus gros poids
        lignes[theme] = ", ".join(vocabulaire[i] for i in meilleurs)
    return pd.Series(lignes, name="mots qui comptent le plus")


def pages_les_plus_probables(modele, pages, theme, nb=5):
    """Les nb pages que le modèle juge les plus probables pour un thème, avec leur probabilité."""
    colonne = list(modele.classes_).index(theme)
    probabilites = modele.predict_proba(pages["texte"])[:, colonne]
    resultat = pages[["page"]].assign(probabilite=probabilites.round(2))
    return resultat.sort_values("probabilite", ascending=False).head(nb)
