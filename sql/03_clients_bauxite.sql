-- Les acheteurs de bauxite guinéenne sur deux années, pour voir comment la clientèle a changé.
-- La part est calculée au sein de chaque année (PARTITION BY annee).
SELECT annee,
       pays_importateur,
       ROUND(valeur_usd / 1e6) AS millions_usd,
       ROUND(100 * valeur_usd / SUM(valeur_usd) OVER (PARTITION BY annee), 1) AS part_pct
FROM '{data}/comtrade_miroir.csv'
WHERE produit = 'bauxite' AND annee IN ({debut}, {fin})
QUALIFY ROW_NUMBER() OVER (PARTITION BY annee ORDER BY valeur_usd DESC) <= 6
ORDER BY annee, valeur_usd DESC;
