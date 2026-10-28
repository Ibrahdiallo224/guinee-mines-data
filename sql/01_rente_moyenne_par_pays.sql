-- Rente minière moyenne et maximale par pays, 2000-2018 (Banque mondiale)
SELECT pays,
       ROUND(AVG(valeur), 1) AS rente_moyenne_2000_2018,
       ROUND(MAX(valeur), 1) AS rente_max
FROM '{data}/rente_miniere.csv'
WHERE annee BETWEEN 2000 AND 2018
GROUP BY pays
ORDER BY rente_moyenne_2000_2018 DESC;
