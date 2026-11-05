"""Préparer les pages des rapports ITIE pour entraîner un modèle qui reconnaît le thème d'une page.

L'idée : le sommaire du rapport dit à quelle section appartient chaque page.
On s'en sert comme étiquettes « gratuites » : pas besoin d'annoter 800 pages à la main.
"""
import re
from collections import Counter

import pandas as pd
import pdfplumber

# « 4.1    Contexte du secteur minier ........ 22 » -> section 4.1, page 22
LIGNE_SOMMAIRE = re.compile(r"^\s*(\d+(?:\.\d+)?|ANNEXES)\s+(.*?)[\s.]*\.{3,}\s*(\d+)\s*$")
# le pied de page : « MOORE INSIGHT 19 ITIE Guinée »
PIED_DE_PAGE = re.compile(r"MOORE INSIGHT\s+(\d+)")


def lire_pages(chemin):
    """Le texte de chaque page du PDF, dans une liste (la page 1 est à l'indice 0)."""
    with pdfplumber.open(chemin) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


def sommaire(pages, nb_pages=4):
    """Lit la table des matières (dans les premières pages) : liste de (section, titre, page imprimée)."""
    entrees = []
    for texte in pages[:nb_pages]:
        for ligne in texte.split("\n"):
            m = LIGNE_SOMMAIRE.match(ligne)
            if m:
                entrees.append((m.group(1), m.group(2), int(m.group(3))))
    return entrees


def decalage(pages):
    """Écart entre le numéro de la page dans le PDF et le numéro imprimé en bas de la page.

    Exemple : la page imprimée 19 est la 21e page du PDF, l'écart est 2.
    On prend l'écart le plus fréquent sur tout le rapport.
    """
    ecarts = Counter()
    for i, texte in enumerate(pages):
        m = PIED_DE_PAGE.search(texte)
        if m:
            ecarts[i + 1 - int(m.group(1))] += 1
    return ecarts.most_common(1)[0][0]


def theme_de_la_section(section, themes):
    """Cherche le thème de « 4.3 » dans le dictionnaire ; sinon celui du chapitre « 4 »."""
    return themes.get(section, themes.get(section.split(".")[0]))


def pages_etiquetees(chemin, annee, themes):
    """Un tableau avec une ligne par page : année, page, section, thème et texte.

    On garde les pages des chapitres 1 à 8. On enlève la couverture, le sommaire, les annexes
    (listes de titres miniers…) et les pages sans texte (images scannées).
    """
    pages = lire_pages(chemin)
    entrees = sommaire(pages)
    ecart = decalage(pages)
    lignes = []
    for i, texte in enumerate(pages):
        page_imprimee = i + 1 - ecart
        avant = [e for e in entrees if e[2] <= page_imprimee]   # les sections qui commencent avant cette page
        if not avant or len(texte) < 100:
            continue
        section = avant[-1][0]                                   # la dernière : c'est la section de la page
        if section == "ANNEXES":
            continue
        lignes.append({"annee": annee, "page": i + 1, "section": section,
                       "theme": theme_de_la_section(section, themes), "texte": texte})
    return pd.DataFrame(lignes)
