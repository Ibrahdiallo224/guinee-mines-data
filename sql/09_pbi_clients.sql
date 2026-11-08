-- Ce que chaque pays déclare avoir importé de Guinée, par produit et par année, en millions de dollars (UN Comtrade miroir).
SELECT annee, produit, pays_importateur AS pays, iso3, SUM(valeur_usd) / 1e6 AS valeur_musd
FROM '{data}/comtrade_miroir.csv'
GROUP BY annee, produit, pays_importateur, iso3
ORDER BY annee, produit, valeur_musd DESC;
