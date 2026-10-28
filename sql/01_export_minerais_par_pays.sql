-- Part des minerais et métaux dans les exportations, moyenne jusqu'en 2016 (Banque mondiale).
-- COUNT(valeur) ne compte que les années renseignées.
SELECT pays,
       COUNT(valeur) AS annees_disponibles,
       ROUND(AVG(valeur), 1) AS part_moyenne_pct
FROM '{data}/export_minerais.csv'
WHERE annee <= 2016
GROUP BY pays
ORDER BY part_moyenne_pct DESC;
