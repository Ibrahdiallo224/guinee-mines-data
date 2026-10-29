-- Série d'un pays (ou du monde), en millions de tonnes sèches, au format attendu par src/prevision.py.
SELECT annee, production_t / 1e6 AS valeur
FROM '{data}/bauxite_monde.csv'
WHERE pays = '{pays}'
ORDER BY annee;
