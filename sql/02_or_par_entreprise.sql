-- Production d'or par entreprise (kg) et part de chacune la dernière année
SELECT entreprise,
       SUM(production_kg) FILTER (WHERE annee = 2019) AS kg_2019,
       SUM(production_kg) FILTER (WHERE annee = 2023) AS kg_2023,
       SUM(production_kg) FILTER (WHERE annee = 2024) AS kg_2024,
       ROUND(100 * SUM(production_kg) FILTER (WHERE annee = 2024)
             / SUM(SUM(production_kg) FILTER (WHERE annee = 2024)) OVER (), 1) AS part_2024_pct
FROM '{data}/or_par_entreprise.csv'
GROUP BY entreprise
ORDER BY kg_2024 DESC NULLS LAST;
