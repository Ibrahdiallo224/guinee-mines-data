-- Prix moyen payé par la Chine pour une tonne de bauxite guinéenne (valeur CIF / poids).
-- On écarte les années où le poids a été estimé : le prix calculé n'aurait pas de sens.
SELECT annee,
       valeur_usd / (poids_kg / 1000) AS usd_par_tonne,
       poids_kg / 1e9 AS millions_tonnes
FROM '{data}/comtrade_miroir.csv'
WHERE produit = 'bauxite' AND iso3 = 'CHN' AND NOT poids_estime
ORDER BY annee;
