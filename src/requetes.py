"""Lance les requêtes SQL du dossier sql/ avec DuckDB.

Chaque requête est un fichier .sql. Dans le texte :
- {data} est remplacé par le chemin du dossier data/ ;
- les autres {paramètres} (par exemple {annee}) sont passés à la fonction.
"""
from pathlib import Path

import duckdb

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_SQL = RACINE / "sql"
DOSSIER_DATA = RACINE / "data"


def requete(nom, **parametres):
    """Lit sql/<nom>.sql, remplace les paramètres et renvoie le résultat DuckDB.

    Exemple : requete("02_parts_entreprises", annee=2024).df()
    """
    texte = (DOSSIER_SQL / f"{nom}.sql").read_text(encoding="utf-8")
    texte = texte.replace("{data}", DOSSIER_DATA.as_posix())
    for cle, valeur in parametres.items():
        texte = texte.replace("{" + cle + "}", str(valeur))
    return duckdb.sql(texte)
