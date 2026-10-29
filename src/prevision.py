"""Prévisions par régression linéaire (scikit-learn).

Une série = un tableau avec deux colonnes : annee et valeur.
"""
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


def entrainer(serie, debut, fin):
    """Ajuste une droite sur les années de debut à fin (incluses) et renvoie le modèle."""
    donnees = serie[(serie["annee"] >= debut) & (serie["annee"] <= fin)]
    modele = LinearRegression()
    modele.fit(donnees[["annee"]], donnees["valeur"])     # X doit être un tableau à 2 dimensions
    return modele


def tester(serie, debut, fin_entrainement):
    """Entraîne jusqu'à fin_entrainement, prédit les années suivantes et mesure l'erreur.

    Le modèle ne voit jamais les années de test : c'est ce qui rend la mesure honnête.
    """
    modele = entrainer(serie, debut, fin_entrainement)
    test = serie[serie["annee"] > fin_entrainement].copy()
    test["prevision"] = modele.predict(test[["annee"]])
    test["erreur_pct"] = 100 * (test["prevision"] - test["valeur"]) / test["valeur"]
    erreur_moyenne = mean_absolute_error(test["valeur"], test["prevision"])
    return test, erreur_moyenne


def prevoir(serie, debut, fin, horizon):
    """Prévision jusqu'à l'année horizon, avec un intervalle de prédiction à 95 %.

    L'intervalle s'élargit quand on s'éloigne des données : plus on prévoit loin, moins on est sûr.
    """
    donnees = serie[(serie["annee"] >= debut) & (serie["annee"] <= fin)]
    modele = entrainer(serie, debut, fin)
    x = donnees["annee"].to_numpy()
    residus = donnees["valeur"] - modele.predict(donnees[["annee"]])
    n = len(x)
    ecart_type = np.sqrt((residus ** 2).sum() / (n - 2))
    t = stats.t.ppf(0.975, n - 2)

    futur = pd.DataFrame({"annee": range(fin + 1, horizon + 1)})
    futur["prevision"] = modele.predict(futur[["annee"]])
    marge = t * ecart_type * np.sqrt(1 + 1 / n + (futur["annee"] - x.mean()) ** 2 / ((x - x.mean()) ** 2).sum())
    futur["bas"] = futur["prevision"] - marge
    futur["haut"] = futur["prevision"] + marge
    return futur, modele


ONCE_PAR_KG = 32.1507    # 1 kg = 32,15 onces troy (unité du prix de l'or)


def synthese(bauxite, orr, prix, fer):
    """Valeur des exportations minières en milliards de dollars, pour l'année d'horizon.

    bauxite, orr : la ligne de la prévision pour cette année (colonnes prevision, bas, haut)
    prix         : tableau produit / prix (data/prix_reference.csv)
    fer          : valeurs de Simandou à plein régime selon les 3 prix (étape 4), en milliards
    """
    p = prix.set_index("produit")["prix"]
    lignes = [
        ("Bauxite", bauxite["bas"] * p["bauxite"] / 1000, bauxite["prevision"] * p["bauxite"] / 1000,
         bauxite["haut"] * p["bauxite"] / 1000),
        ("Or industriel", orr["bas"] * 1000 * ONCE_PAR_KG * p["or"] / 1e9,
         orr["prevision"] * 1000 * ONCE_PAR_KG * p["or"] / 1e9, orr["haut"] * 1000 * ONCE_PAR_KG * p["or"] / 1e9),
        ("Fer (Simandou)", fer["bas"], fer["moyen"], fer["haut"]),
    ]
    tableau = pd.DataFrame(lignes, columns=["produit", "bas", "central", "haut"])
    tableau.loc[len(tableau)] = ["Total", tableau["bas"].sum(), tableau["central"].sum(), tableau["haut"].sum()]
    return tableau


def part_prevue(prevision_pays, prevision_monde):
    """Part d'un pays dans la production mondiale prévue, en %, année par année."""
    part = prevision_pays[["annee"]].copy()
    part["part_pct"] = 100 * prevision_pays["prevision"] / prevision_monde["prevision"]
    return part
