-- Ce que le monde achète à la Guinée, par produit (milliards de dollars, données miroir).
SELECT annee,
       SUM(valeur_usd) FILTER (WHERE produit = 'bauxite') / 1e9 AS bauxite,
       SUM(valeur_usd) FILTER (WHERE produit = 'or') / 1e9 AS orr,
       SUM(valeur_usd) FILTER (WHERE produit = 'alumine') / 1e9 AS alumine,
       SUM(valeur_usd) FILTER (WHERE produit = 'minerai de fer') / 1e9 AS fer
FROM '{data}/comtrade_miroir.csv'
GROUP BY annee
ORDER BY annee;
