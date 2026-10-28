-- Valeur de la bauxite importée depuis la Guinée, par année, et part de la Chine.
-- Données miroir : ce que les pays acheteurs déclarent avoir importé (valeur CIF, en dollars).
SELECT annee,
       COUNT(*) AS pays_acheteurs,
       SUM(valeur_usd) / 1e9 AS total_milliards_usd,
       SUM(valeur_usd) FILTER (WHERE iso3 = 'CHN') / 1e9 AS chine_milliards_usd,
       100 * SUM(valeur_usd) FILTER (WHERE iso3 = 'CHN') / SUM(valeur_usd) AS part_chine_pct
FROM '{data}/comtrade_miroir.csv'
WHERE produit = 'bauxite'
GROUP BY annee
ORDER BY annee;
