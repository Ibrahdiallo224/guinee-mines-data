-- Acheteurs d'or guinéen par année (millions de dollars) : Émirats, Inde, Suisse, autres.
SELECT annee,
       COUNT(*) AS pays_acheteurs,
       COALESCE(SUM(valeur_usd) FILTER (WHERE iso3 = 'ARE'), 0) / 1e6 AS emirats,
       COALESCE(SUM(valeur_usd) FILTER (WHERE iso3 = 'IND'), 0) / 1e6 AS inde,
       COALESCE(SUM(valeur_usd) FILTER (WHERE iso3 = 'CHE'), 0) / 1e6 AS suisse,
       COALESCE(SUM(valeur_usd) FILTER (WHERE iso3 NOT IN ('ARE', 'IND', 'CHE')), 0) / 1e6 AS autres,
       SUM(valeur_usd) / 1e6 AS total
FROM '{data}/comtrade_miroir.csv'
WHERE produit = 'or'
GROUP BY annee
ORDER BY annee;
