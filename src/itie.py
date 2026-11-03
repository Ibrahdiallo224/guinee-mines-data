"""Lecture des rapports ITIE Guinée (PDF) avec pdfplumber.

Le texte d'un PDF n'est qu'une suite de mots posés sur la page, chacun avec sa position.
Pour reconstruire un tableau, on regroupe les mots par ligne (même hauteur),
puis par cellule (mots très proches les uns des autres).
"""
import re

import pandas as pd
import pdfplumber

ECART_MAX_DANS_UN_NOMBRE = 3   # en points : dans « 955 845 476 », les morceaux sont à 2,4 points ; deux colonnes, à 3,8 points ou plus


def nombre(texte):
    """Convertit un montant du rapport en nombre : « (32 384 338 373) » -> -32384338373, « - » -> 0."""
    texte = texte.replace(" ", "")
    if texte in ("-", ""):
        return 0
    negatif = texte.startswith("(")                    # les montants négatifs sont entre parenthèses
    texte = texte.strip("()").replace(",", ".")        # « 335,5 » : la virgule est le séparateur décimal
    valeur = round(float(texte))                       # on arrondit au franc près
    return -valeur if negatif else valeur


def est_un_montant(mot):
    """Vrai si le mot ressemble à un morceau de montant : 955, (32, 373), 335,5) ou -."""
    return re.fullmatch(r"\(?\d{1,3}(,\d+)?\)?|-", mot) is not None


def trouver_page(chemin, titre, a_partir_de=20):
    """Numéro (à partir de 1) de la première page qui contient le titre, en sautant le sommaire."""
    with pdfplumber.open(chemin) as pdf:
        for i in range(a_partir_de, len(pdf.pages)):
            if titre in (pdf.pages[i].extract_text() or ""):
                return i + 1
    return None


def lignes(page):
    """Regroupe les mots de la page en lignes : une ligne = des mots à la même hauteur."""
    resultat = []
    for mot in page.extract_words():
        if resultat and abs(mot["top"] - resultat[-1][0]["top"]) < 3:
            resultat[-1].append(mot)
        else:
            resultat.append([mot])
    return resultat


def cellules(ligne):
    """Coupe une ligne en texte (le nom) et en montants (mots proches regroupés).

    Chaque montant est gardé avec sa position horizontale de fin (x1) : les montants sont alignés
    à droite dans leur colonne, c'est ce qui permet de savoir à quelle colonne ils appartiennent.
    """
    nom, montants = [], []
    precedent = None
    for mot in ligne:
        if est_un_montant(mot["text"]) and (montants or nom):
            colle = precedent is not None and mot["x0"] - precedent["x1"] < ECART_MAX_DANS_UN_NOMBRE
            suite = (colle and montants and est_un_montant(precedent["text"])
                     and "-" not in (precedent["text"], mot["text"])
                     and not mot["text"].startswith("(")          # une parenthèse ouvre toujours un nouveau nombre
                     and not montants[-1]["texte"].endswith(")"))  # une parenthèse fermante termine le nombre
            if suite:
                montants[-1]["texte"] += " " + mot["text"]      # même nombre : on recolle « 955 » et « 845 »
                montants[-1]["x1"] = mot["x1"]
            else:
                montants.append({"texte": mot["text"], "x1": mot["x1"]})   # nouvelle colonne
        else:
            nom.append(mot["text"])
        precedent = mot
    return " ".join(nom), montants


def est_un_entete(texte):
    """Vrai pour les morceaux d'en-tête comme « (a b) » ou « (c) = »."""
    return re.search(r"\([a-i]\b|\b[a-i]\)", texte) is not None


def paiements_par_societe(chemin, numero_page, annee):
    """Lit le tableau « Rapprochement des flux de paiement par société » et renvoie un tableau pandas.

    Colonnes gardées : déclaration de la société et de l'État, avant et après ajustements.
    """
    with pdfplumber.open(chemin) as pdf:
        page = pdf.pages[numero_page - 1]
        rangees, morceaux_de_nom = [], []
        for ligne in lignes(page):
            nom, montants = cellules(ligne)
            if len(montants) >= 6:                              # une ligne de chiffres = une société (ou le total)
                mots = nom.split()
                numero = mots[0] if mots and mots[0].isdigit() else ""
                rangees.append({"y": ligne[0]["top"], "no": numero,
                                "nom": " ".join(mots[1:] if numero else mots), "montants": montants})
            elif nom and not est_un_entete(nom):
                morceaux_de_nom.append((ligne[0]["top"], nom))  # morceau de nom écrit sur une autre ligne
        # les traits horizontaux du tableau séparent les sociétés
        traits = sorted({round(t["top"]) for t in page.edges if t["orientation"] == "h" and t["x1"] - t["x0"] > 100})

    # 1. Les colonnes : on prend la ligne Total, la seule où toutes les colonnes sont remplies
    total = [r for r in rangees if r["nom"].startswith("Total")][0]
    colonnes = [m["x1"] for m in total["montants"]]

    # 2. Les noms trop longs sont coupés sur plusieurs lignes. Chaque morceau va à la société
    #    qui se trouve entre les deux mêmes traits horizontaux (la même « case » du tableau) ;
    #    s'il n'y en a pas, à la société la plus proche.
    def case(y):
        return sum(1 for t in traits if t <= y + 1)        # nombre de traits au-dessus = numéro de la case
    for r in rangees:
        r["morceaux"] = [(r["y"], r["nom"])]
    for y, morceau in morceaux_de_nom:
        cibles = [r for r in rangees if case(r["y"]) == case(y)] or \
                 [r for r in rangees if abs(r["y"] - y) < 15]
        if cibles:
            cible = min(cibles, key=lambda r: abs(r["y"] - y))
            cible["morceaux"].append((y, morceau))
    for r in rangees:
        r["nom"] = " ".join(texte for _, texte in sorted(r["morceaux"]))   # on remet les morceaux de haut en bas

    # 3. Chaque montant va dans la colonne dont la fin (x1) est la plus proche
    societes = []
    for r in rangees:
        valeurs = [0] * len(colonnes)
        for m in r["montants"]:
            i = min(range(len(colonnes)), key=lambda c: abs(colonnes[c] - m["x1"]))
            valeurs[i] = nombre(m["texte"])
        nom = "Total" if r is total else " ".join(r["nom"].split())
        societes.append({"annee": annee, "no": r["no"], "nom": nom,
                         "societe_initial": valeurs[0], "etat_initial": valeurs[1],
                         "societe_ajuste": valeurs[-3], "etat_ajuste": valeurs[-2]})
    return pd.DataFrame(societes)


def verifier_total(tableau):
    """Compare la somme des sociétés avec la ligne Total du rapport, colonne par colonne."""
    total = tableau[tableau["nom"].str.startswith("Total")].iloc[0]
    societes = tableau[~tableau["nom"].str.startswith("Total")]
    for colonne in ("societe_initial", "etat_initial", "societe_ajuste", "etat_ajuste"):
        somme = societes[colonne].sum()
        etat = "OK" if abs(somme - total[colonne]) <= len(societes) else "ÉCART"   # 1 franc d'arrondi par ligne toléré
        print(f"{colonne:16} somme = {somme:>20,}  total du rapport = {total[colonne]:>20,}  {etat}".replace(",", " "))
