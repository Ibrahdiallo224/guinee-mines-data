-- Valeur des exportations de Simandou de 2026 à 2030 : chaque année combinée avec chacun des 3 prix.
-- CROSS JOIN associe chaque ligne de la 1re table à chaque ligne de la 2e : 5 années x 3 prix = 15 lignes.
WITH volumes AS (
    SELECT CAST(cle AS INTEGER) AS annee, valeur AS millions_tonnes
    FROM '{data}/hypotheses_simandou.csv'
    WHERE type = 'volume'
),
prix AS (
    SELECT cle AS scenario, valeur AS usd_par_tonne
    FROM '{data}/hypotheses_simandou.csv'
    WHERE type = 'prix'
)
SELECT annee, scenario, millions_tonnes, usd_par_tonne,
       millions_tonnes * usd_par_tonne / 1000 AS milliards_usd
FROM volumes
CROSS JOIN prix
ORDER BY annee, usd_par_tonne;
