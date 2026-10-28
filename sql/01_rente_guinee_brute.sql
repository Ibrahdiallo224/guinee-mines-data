-- Rente minière de la Guinée sans correction, pour montrer l'anomalie 2019-2021
SELECT annee, ROUND(valeur, 1) AS rente_pct_pib
FROM '{data}/rente_miniere.csv'
WHERE code_pays = 'GIN' AND annee BETWEEN 2015 AND 2025
ORDER BY annee;
