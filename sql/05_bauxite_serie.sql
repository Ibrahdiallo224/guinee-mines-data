-- Production de bauxite de 2000 à 2024, en millions de tonnes (USGS puis Ministère des Mines).
SELECT annee, production_t / 1e6 AS valeur
FROM '{data}/bauxite_production_longue.csv'
ORDER BY annee;
