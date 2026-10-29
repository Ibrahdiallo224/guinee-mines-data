"""Graphiques du projet Guinée Mines Data.

Toutes les fonctions partagent le même style : Guinée en rouge, voisins en gris,
titre qui dit la conclusion, source en bas à gauche.
"""
from pathlib import Path

import matplotlib.pyplot as plt

DOSSIER_IMAGES = Path(__file__).resolve().parent.parent / "images"

GUINEE = "#c0392b"   # couleur de la Guinée dans tout le projet
GRIS = "#b0b0b0"
BAUXITE = "#b5651d"
OR = "#d4af37"
ALUMINE = "#7f8c8d"

NOMS_PAYS = {"Guinea": "Guinée", "Mali": "Mali", "Sierra Leone": "Sierra Leone",
             "Senegal": "Sénégal", "Cote d'Ivoire": "Côte d'Ivoire"}

plt.rcParams.update({
    "figure.figsize": (10, 5.5),
    "font.size": 11,
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.alpha": 0.3,
})


def ajouter_source(texte):
    """Écrit la source en bas à gauche du graphique."""
    plt.figtext(0.01, -0.02, "Source : " + texte, fontsize=9, color="gray")


def enregistrer(nom_fichier):
    """Enregistre le graphique dans images/ puis l'affiche."""
    DOSSIER_IMAGES.mkdir(exist_ok=True)
    plt.savefig(DOSSIER_IMAGES / nom_fichier, dpi=150, bbox_inches="tight")
    plt.show()


def graphique_rente(tableau):
    """Courbes de rente minière : une colonne par pays, une ligne par année."""
    fig, ax = plt.subplots()
    for pays in tableau.columns:
        serie = tableau[pays].dropna()
        est_guinee = pays == "Guinea"
        ax.plot(serie.index, serie.values,
                color=GUINEE if est_guinee else GRIS,
                linewidth=3 if est_guinee else 1.5)
        # le nom du pays au bout de sa courbe, plutôt qu'une légende
        decalage = {"Senegal": 0.35, "Cote d'Ivoire": -0.35}.get(pays, 0)
        ax.text(serie.index[-1] + 0.3, serie.values[-1] + decalage, NOMS_PAYS[pays],
                color=GUINEE if est_guinee else "gray",
                fontweight="bold" if est_guinee else "normal", va="center")

    ax.annotate("9,8 % en 2017", xy=(2017, tableau.loc[2017, "Guinea"]),
                xytext=(2009.5, 10.5), color=GUINEE,
                arrowprops={"arrowstyle": "->", "color": GUINEE})
    ax.axvspan(2018.5, 2021.5, color=GUINEE, alpha=0.07)
    ax.text(2020, 12.5, "Guinée : données\nmanquantes", ha="center", color=GUINEE, fontsize=9)

    ax.set_title("2000-2018 : la Guinée, l'économie la plus dépendante des mines de la région")
    ax.set_ylabel("Rente minière (% du PIB)")
    ax.set_xlim(2000, 2023.5)
    ajouter_source("Banque mondiale, indicateur NY.GDP.MINR.RT.ZS")
    enregistrer("rente_miniere_voisins.png")


def graphique_exportations(exports):
    """Barres empilées : part de la bauxite, de l'or et de l'alumine dans les exportations."""
    t = exports.set_index("annee")
    annees = t.index.astype(str)
    fig, ax = plt.subplots()
    bas = 0
    for colonne, nom, couleur in [("bauxite_pct", "Bauxite", BAUXITE),
                                  ("or_pct", "Or", OR),
                                  ("alumine_pct", "Alumine", ALUMINE)]:
        ax.bar(annees, t[colonne], bottom=bas, label=nom, color=couleur, width=0.6)
        bas = bas + t[colonne]
    for annee, total in zip(annees, t["mines_pct"]):
        ax.text(annee, total + 1.5, f"{total:.0f} %", ha="center", fontweight="bold")

    ax.set_title("Plus de 85 % des exportations guinéennes viennent des mines", pad=30)
    ax.set_ylabel("% de la valeur des exportations")
    ax.set_ylim(0, 105)
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False)
    ajouter_source("INS Guinée, Note d'analyse du commerce extérieur 2024")
    enregistrer("exportations_minieres.png")


def graphique_bauxite(bauxite):
    """Barres des exportations de bauxite (millions de tonnes) ; la dernière année est une estimation."""
    annees = bauxite["annee"].astype(str)
    valeurs = bauxite["millions_tonnes"]
    facteur = f"{valeurs.iloc[-1] / valeurs.iloc[0]:.1f}".replace(".", ",")

    fig, ax = plt.subplots()
    barres = ax.bar(annees, valeurs, color=BAUXITE, width=0.6)
    barres[-1].set_alpha(0.45)
    barres[-1].set_hatch("//")
    for annee, v in zip(annees, valeurs):
        ax.text(annee, v + 3, f"{v:.0f}", ha="center", fontweight="bold")
    ax.text(len(annees) - 1, valeurs.iloc[-1] + 14, "annonce officielle", ha="center", fontsize=9, color="gray")

    ax.set_title(f"Exportations de bauxite : ×{facteur} entre {annees.iloc[0]} et {annees.iloc[-1]}")
    ax.set_ylabel("Millions de tonnes")
    ax.set_ylim(0, valeurs.max() * 1.2)
    ajouter_source("Ministère des Mines (2019-2024) ; annonce officielle relayée par la presse (2025)")
    enregistrer("bauxite_exportations.png")


# ---------- Étape 2 : entreprises ----------

def graphique_parts_entreprises(parts, annee):
    """Barres horizontales : part de chaque entreprise dans les exportations de bauxite."""
    parts = parts.sort_values("part_pct")
    couleurs = [BAUXITE if i >= len(parts) - 3 else GRIS for i in range(len(parts))]   # top 3 en couleur
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.barh(parts["entreprise"], parts["part_pct"], color=couleurs)
    for y, (p, mt) in enumerate(zip(parts["part_pct"], parts["millions_tonnes"])):
        etiquette = f"{p:.0f} %" if p >= 1 else "<1 %"
        ax.text(p + 0.5, y, f"{etiquette}  ({mt:.1f} Mt)".replace(".", ","), va="center", fontsize=10)
    ax.grid(False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    premier = parts.iloc[-1]
    ax.set_title(f"{premier['entreprise']} exporte à elle seule {premier['part_pct']:.0f} % "
                 f"de la bauxite guinéenne ({annee})")
    ajouter_source(f"Ministère des Mines, Bulletin annuel {annee}")
    enregistrer("bauxite_parts_entreprises.png")


def graphique_evolution_entreprises(tableau, a_souligner):
    """Courbes 2019-2024 des exportations par entreprise ; une colonne par entreprise."""
    couleurs = {a_souligner[0]: BAUXITE, a_souligner[1]: GUINEE}
    fig, ax = plt.subplots()
    for entreprise in tableau.columns:
        serie = tableau[entreprise].dropna()
        mise_en_avant = entreprise in couleurs
        ax.plot(serie.index, serie.values, marker="o", markersize=4,
                color=couleurs.get(entreprise, GRIS), linewidth=3 if mise_en_avant else 1.5)
        decalage = {"CBG": 0.7, "CHALCO": -0.5, "GAC": 0.6, "CDM CHINE": -0.6}.get(entreprise, 0)
        ax.text(serie.index[-1] + 0.1, serie.values[-1] + decalage, entreprise, va="center",
                color=couleurs.get(entreprise, "gray"),
                fontweight="bold" if mise_en_avant else "normal")
    ax.set_title(f"{a_souligner[0]} accélère, {a_souligner[1]} surgit en quatre ans")
    ax.set_ylabel("Exportations de bauxite (millions de tonnes)")
    ax.set_xlim(tableau.index.min() - 0.2, tableau.index.max() + 1.1)
    ax.set_xticks(tableau.index)
    ajouter_source("Ministère des Mines, Annuaire statistique 2023 et Bulletin annuel 2024")
    enregistrer("bauxite_evolution_entreprises.png")


def graphique_taxe_par_tonne(taxes, annee):
    """Barres horizontales : taxe minière payée par tonne de bauxite exportée."""
    taxes = taxes.sort_values("usd_par_tonne")
    moyenne = (taxes["taxe_miniere_usd"].sum() / taxes["exportation_t"].sum())
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh(taxes["entreprise"], taxes["usd_par_tonne"], color=BAUXITE)
    for y, v in enumerate(taxes["usd_par_tonne"]):
        ax.text(v + 0.05, y, f"{v:.2f} $".replace(".", ","), va="center", fontsize=10)
    ax.axvline(moyenne, color=GUINEE, linestyle="--", linewidth=1.5)
    ax.text(moyenne + 0.05, -0.7, f"moyenne : {moyenne:.2f} $".replace(".", ","),
            color=GUINEE, fontsize=10)
    ax.grid(False)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.set_title(f"Taxe minière payée par tonne de bauxite exportée ({annee})")
    ajouter_source(f"Ministère des Mines, Bulletin annuel {annee} ; CBG et COBAD absentes (pas de taxe minière déclarée)")
    enregistrer("taxe_par_tonne.png")


# ---------- Étape 3 : pays acheteurs ----------

def graphique_chine_bauxite(t):
    """Barres empilées : valeur de la bauxite achetée par la Chine et par les autres pays."""
    annees = t["annee"].astype(str)
    autres = t["total_milliards_usd"] - t["chine_milliards_usd"]
    fig, ax = plt.subplots()
    ax.bar(annees, t["chine_milliards_usd"], color=BAUXITE, width=0.65, label="Chine")
    ax.bar(annees, autres, bottom=t["chine_milliards_usd"], color=GRIS, width=0.65, label="Autres pays")
    for annee, total, part in zip(annees, t["total_milliards_usd"], t["part_chine_pct"]):
        ax.text(annee, total + 0.25, f"{part:.0f} %", ha="center", fontweight="bold", color=BAUXITE)
    ax.set_title(f"La Chine achète {t['part_chine_pct'].iloc[-1]:.0f} % de la bauxite guinéenne "
                 f"en {annees.iloc[-1]}", pad=30)
    ax.set_ylabel("Milliards de dollars (valeur à l'arrivée)")
    ax.set_ylim(0, t["total_milliards_usd"].max() * 1.12)
    ax.legend(ncol=2, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
    ax.text(1, 1.02, "en gras : part de la Chine", transform=ax.transAxes, ha="right",
            fontsize=9, color="gray")
    ajouter_source("UN Comtrade, importations déclarées depuis la Guinée (code SH 2606)")
    enregistrer("bauxite_chine.png")


def graphique_prix_tonne(prix):
    """Courbe du prix moyen d'une tonne de bauxite guinéenne à son arrivée en Chine."""
    prix = prix[prix["millions_tonnes"] > 1]          # 2015 : moins d'1 Mt, prix peu représentatif
    toutes = range(prix["annee"].min(), prix["annee"].max() + 1)
    courbe = prix.set_index("annee")["usd_par_tonne"].reindex(toutes)   # année exclue = trou dans la courbe
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(courbe.index, courbe.values, color=BAUXITE, linewidth=3, marker="o")
    for annee, v in zip(prix["annee"], prix["usd_par_tonne"]):
        ax.text(annee, v + 2, f"{v:.0f} $", ha="center", fontsize=10)
    ax.set_title("Une tonne de bauxite guinéenne vaut 81 $ à son arrivée en Chine (2025)")
    ax.set_ylabel("Dollars par tonne (valeur CIF)")
    ax.set_ylim(0, prix["usd_par_tonne"].max() * 1.2)
    ax.set_xticks(toutes)
    ajouter_source("UN Comtrade (valeur / poids déclarés par la Chine) ; 2016 et 2023 exclues : poids estimés")
    enregistrer("bauxite_prix_chine.png")


def graphique_or_clients(t):
    """Barres empilées : valeur de l'or acheté à la Guinée, par pays acheteur."""
    annees = t["annee"].astype(str)
    fig, ax = plt.subplots()
    bas = 0
    for colonne, nom, couleur in [("emirats", "Émirats arabes unis", OR),
                                  ("inde", "Inde", "#8e6c3a"),
                                  ("suisse", "Suisse", ALUMINE),
                                  ("autres", "Autres", GRIS)]:
        ax.bar(annees, t[colonne] / 1000, bottom=bas, label=nom, color=couleur, width=0.65)
        bas = bas + t[colonne] / 1000
    ax.axvspan(len(annees) - 2.5, len(annees) - 0.5, color=GUINEE, alpha=0.07)
    ax.text(len(annees) - 1.5, t["total"].max() / 1000 * 0.55,
            "Émirats absents\ndes déclarations\n(données\nincomplètes)",
            ha="center", color=GUINEE, fontsize=9)
    ax.set_title("L'or guinéen part surtout vers les Émirats (Dubaï)", pad=30)
    ax.set_ylabel("Milliards de dollars")
    ax.legend(ncol=4, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
    ajouter_source("UN Comtrade, importations déclarées depuis la Guinée (code SH 7108)")
    enregistrer("or_clients.png")


# ---------- Étape 4 : Simandou ----------

FER = "#34495e"


def graphique_simandou_scenarios(scenarios):
    """Valeur des exportations de Simandou 2026-2030 : prix moyen en trait plein, bas et haut en fourchette."""
    t = scenarios.pivot(index="annee", columns="scenario", values="milliards_usd")
    fig, ax = plt.subplots()
    ax.fill_between(t.index, t["bas"], t["haut"], color=FER, alpha=0.15, label="fourchette prix bas / haut")
    ax.plot(t.index, t["moyen"], color=FER, linewidth=3, marker="o", label="prix moyen (97 $/t)")
    for annee, v in t["moyen"].items():
        ax.text(annee, v + 0.6, f"{v:.1f}".replace(".", ","), ha="center", fontweight="bold", color=FER)
    ax.text(t.index[-1] + 0.08, t["haut"].iloc[-1], "prix haut\n(110 $/t)", va="center", fontsize=9, color="gray")
    ax.text(t.index[-1] + 0.08, t["bas"].iloc[-1], "prix bas\n(80 $/t)", va="center", fontsize=9, color="gray")
    ax.set_title("Simandou pourrait exporter 10 à 13 milliards de dollars par an en 2030", pad=30)
    ax.set_ylabel("Milliards de dollars par an")
    ax.set_xticks(t.index)
    ax.set_xlim(t.index.min() - 0.3, t.index.max() + 0.6)
    ax.legend(ncol=2, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
    ajouter_source("Scénario construit à partir des annonces de Rio Tinto (montée en charge) et de la Banque mondiale (prix)")
    enregistrer("simandou_scenarios.png")


def graphique_simandou_comparaison(comparaison):
    """Barres horizontales : Simandou à plein régime à côté de la bauxite et du PIB."""
    t = comparaison.iloc[::-1]          # le PIB en haut
    couleurs = [FER if "Simandou" in e else (BAUXITE if "Bauxite" in e else GRIS) for e in t["element"]]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(t["element"], t["milliards_usd"], color=couleurs)
    for y, v in enumerate(t["milliards_usd"]):
        ax.text(v + 0.3, y, f"{v:.1f} Md$".replace(".", ","), va="center", fontsize=10)
    ax.grid(False)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.set_title("À plein régime, Simandou pèserait autant que toute la bauxite guinéenne")
    ajouter_source("Banque mondiale (PIB), UN Comtrade (bauxite, valeur à l'arrivée), scénarios Simandou")
    enregistrer("simandou_comparaison.png")


# ---------- Machine learning : prévisions ----------

def graphique_deux_modeles(serie, modele_long, modele_court, debut_court):
    """La série réelle et deux droites de régression : toute la période et depuis la rupture."""
    fig, ax = plt.subplots()
    ax.plot(serie["annee"], serie["valeur"], "o", color=BAUXITE, label="production réelle")
    ax.plot(serie["annee"], modele_long.predict(serie[["annee"]]), "--", color=GRIS, linewidth=2,
            label="droite sur 2000-2024")
    recent = serie[serie["annee"] >= debut_court]
    ax.plot(recent["annee"], modele_court.predict(recent[["annee"]]), color=GUINEE, linewidth=2.5,
            label=f"droite sur {debut_court}-2024")
    ax.axvline(debut_court - 0.5, color="gray", linestyle=":", linewidth=1)
    ax.text(debut_court - 0.7, serie["valeur"].max() * 0.85, "rupture", ha="right", color="gray")
    ax.set_title("Une seule droite ne colle pas : la production change de régime en 2016", pad=30)
    ax.set_ylabel("Millions de tonnes")
    ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
    ajouter_source("USGS Minerals Yearbook (2000-2018), Ministère des Mines (2019-2024)")
    enregistrer("bauxite_deux_modeles.png")


def graphique_prevision(serie, prevision, titre, unite, couleur, source, nom_fichier):
    """La série réelle, puis la prévision avec son intervalle à 95 %."""
    fig, ax = plt.subplots()
    ax.plot(serie["annee"], serie["valeur"], color=couleur, linewidth=2.5, marker="o", markersize=4,
            label="réel")
    ax.plot(prevision["annee"], prevision["prevision"], color=couleur, linewidth=2.5, linestyle="--",
            label="prévision")
    ax.fill_between(prevision["annee"], prevision["bas"], prevision["haut"], color=couleur, alpha=0.15,
                    label="intervalle à 95 %")
    fin = prevision.iloc[-1]
    decimales = 0 if fin["prevision"] >= 100 else 1
    etiquette = f"{fin['prevision']:.{decimales}f}\n({fin['bas']:.{decimales}f} à {fin['haut']:.{decimales}f})"
    ax.text(fin["annee"] + 0.3, fin["prevision"], etiquette.replace(".", ","), va="center", color=couleur,
            fontweight="bold")
    ax.set_title(titre, pad=30)
    ax.set_ylabel(unite)
    ax.set_ylim(0, None)
    ax.set_xlim(serie["annee"].min() - 0.5, fin["annee"] + 3)
    ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
    ajouter_source(source)
    enregistrer(nom_fichier)


def graphique_synthese(tableau, annee):
    """Barres empilées : exportations minières prévues par produit, avec la fourchette du total."""
    produits = tableau[tableau["produit"] != "Total"]
    total = tableau[tableau["produit"] == "Total"].iloc[0]
    couleurs = {"Bauxite": BAUXITE, "Or industriel": OR, "Fer (Simandou)": "#34495e"}
    fig, ax = plt.subplots(figsize=(10, 5))
    gauche = 0
    for _, ligne in produits.iterrows():
        ax.barh(0, ligne["central"], left=gauche, color=couleurs[ligne["produit"]], height=0.5)
        texte = f"{ligne['produit']}\n{ligne['central']:.1f} Md$".replace(".", ",")
        if ligne["central"] >= 5:          # assez de place : texte dans la barre
            ax.text(gauche + ligne["central"] / 2, 0, texte, ha="center", va="center", color="white",
                    fontweight="bold", fontsize=10)
        else:                              # barre étroite : texte sous la barre
            ax.text(gauche + ligne["central"] / 2, -0.42, texte, ha="center", va="center",
                    color=couleurs[ligne["produit"]], fontweight="bold", fontsize=10)
        gauche += ligne["central"]
    ax.errorbar(total["central"], 0.36, xerr=[[total["central"] - total["bas"]], [total["haut"] - total["central"]]],
                fmt="o", color="black", capsize=6, elinewidth=1.5, markersize=4)
    ax.text(total["central"], 0.5, f"Total : {total['central']:.0f} Md$ (fourchette {total['bas']:.0f} à {total['haut']:.0f})",
            ha="center", fontweight="bold")
    ax.set_yticks([])
    ax.set_ylim(-0.6, 0.7)
    ax.set_xlabel("Milliards de dollars par an")
    ax.grid(axis="x", alpha=0.3)
    ax.spines["left"].set_visible(False)
    ax.set_title(f"Exportations minières de la Guinée en {annee} : environ {total['central']:.0f} milliards de dollars")
    ajouter_source("Prévisions (bauxite, or), scénario Simandou (fer), prix UN Comtrade et Banque mondiale")
    enregistrer("synthese_2035.png")


# ---------- Comparaison internationale ----------

def graphique_bauxite_pays(t):
    """Production de bauxite de la Guinée face aux deux autres géants (Australie, Chine)."""
    fig, ax = plt.subplots()
    ax.plot(t["annee"], t["australie"], color="#7f8c8d", linewidth=2, label="Australie")
    ax.plot(t["annee"], t["chine"], color=GRIS, linewidth=2, label="Chine")
    ax.plot(t["annee"], t["guinee"], color=GUINEE, linewidth=3, label="Guinée")
    for colonne, couleur in (("guinee", GUINEE), ("australie", "#7f8c8d"), ("chine", GRIS)):
        fin = t.iloc[-1]
        ax.text(fin["annee"] + 0.3, fin[colonne], f"{fin[colonne]:.0f}", va="center", color=couleur,
                fontweight="bold")
    ax.annotate("2023 : la Guinée\ndépasse l'Australie", xy=(2023, 123), xytext=(2014, 130),
                arrowprops={"arrowstyle": "->", "color": "gray"}, color="gray")
    ax.set_title("Depuis 2023, la Guinée est le premier producteur mondial de bauxite", pad=30)
    ax.set_ylabel("Millions de tonnes sèches")
    ax.set_ylim(0, None)
    ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
    ajouter_source("USGS Minerals Yearbook (2000-2022), Mineral Commodity Summaries 2025 et 2026 (2023-2025)")
    enregistrer("bauxite_pays.png")


def graphique_part_guinee(t, part):
    """Part de la Guinée dans la production mondiale : réel puis prévision."""
    fig, ax = plt.subplots()
    ax.plot(t["annee"], t["part_guinee_pct"], color=GUINEE, linewidth=2.5, marker="o", markersize=4,
            label="réel")
    jonction = [t["annee"].iloc[-1]] + list(part["annee"])
    valeurs = [t["part_guinee_pct"].iloc[-1]] + list(part["part_pct"])
    ax.plot(jonction, valeurs, color=GUINEE, linewidth=2.5, linestyle="--", label="prévision")
    for annee, valeur, decalage in ((2015, t.set_index("annee").loc[2015, "part_guinee_pct"], -4),
                                    (t["annee"].iloc[-1], t["part_guinee_pct"].iloc[-1], 2),
                                    (part["annee"].iloc[-1], part["part_pct"].iloc[-1], 2)):
        ax.text(annee, valeur + decalage, f"{valeur:.0f} %", ha="center", color=GUINEE, fontweight="bold")
    ax.set_title("Une tonne de bauxite sur trois vient de Guinée, bientôt près d'une sur deux", pad=30)
    ax.set_ylabel("% de la production mondiale")
    ax.set_ylim(0, 55)
    ax.legend(ncol=2, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
    ajouter_source("USGS ; prévision : régressions linéaires 2016-2025 sur la Guinée et sur le monde (scikit-learn)")
    enregistrer("part_guinee_monde.png")


# ---------- Simandou face aux autres grandes mines de fer ----------

def graphique_montee_en_charge(t):
    """% de la capacité atteint chaque année : Roy Hill et S11D (réel), Simandou (scénario)."""
    styles = {"Roy Hill": ("#7f8c8d", "-"), "S11D": (GRIS, "-"), "Simandou (scénario)": (GUINEE, "--")}
    fig, ax = plt.subplots()
    for mine, (couleur, trait) in styles.items():
        m = t[t["mine"] == mine]
        ax.plot(m["annee_exploitation"], m["pct_capacite"], color=couleur, linestyle=trait, linewidth=2.5,
                marker="o", label=mine)
        fin = m.iloc[-1]
        ax.text(fin["annee_exploitation"] + 0.15, fin["pct_capacite"] + 3, f"{fin['pct_capacite']:.0f} %",
                va="center", color=couleur, fontweight="bold")
    ax.axhline(100, color="black", linewidth=0.8, linestyle=":")
    ax.set_title("Simandou démarre bien plus lentement que Roy Hill et S11D", pad=30)
    ax.set_xlabel("Année d'exploitation (1 = première année après le démarrage)")
    ax.set_ylabel("% de la capacité annoncée")
    ax.set_ylim(0, 110)
    ax.set_xticks(range(1, 8))
    ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
    ajouter_source("Roy Hill Holdings, Hancock Prospecting, Vale (rapports de production) ; scénario Simandou de l'étape 4")
    enregistrer("simandou_montee_en_charge.png")


def graphique_fer_classement(t, nb=10):
    """Barres horizontales : les plus grands producteurs de fer, avec la Guinée si Simandou tourne à plein."""
    top = t.head(nb).iloc[::-1]          # le premier en haut
    couleurs = [GUINEE if "Guinée" in p else GRIS for p in top["pays"]]
    fig, ax = plt.subplots()
    ax.barh(top["pays"], top["production_mt"], color=couleurs)
    for y, (v, part) in enumerate(zip(top["production_mt"], top["part_monde_pct"])):
        ax.text(v + 10, y, f"{v:.0f} Mt ({part:.1f} %)".replace(".", ","), va="center", fontsize=10)
    ax.grid(False)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.set_xlim(0, top["production_mt"].max() * 1.2)
    ax.set_title("Avec Simandou à plein régime, la Guinée serait le 5e producteur mondial de fer")
    ajouter_source("USGS Mineral Commodity Summaries 2026 (production 2025) ; capacité de Simandou : Rio Tinto")
    enregistrer("fer_classement_mondial.png")
