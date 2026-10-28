-- PIB de la Guinée en milliards de dollars courants (Banque mondiale)
SELECT annee, ROUND(valeur / 1e9, 1) AS pib_milliards_usd
FROM '{data}/pib.csv'
WHERE code_pays = 'GIN' AND annee IN (2000, 2010, 2019, 2023, 2025)
ORDER BY annee;
