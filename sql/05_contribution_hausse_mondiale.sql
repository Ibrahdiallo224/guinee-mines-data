-- Qui a fait monter la production mondiale de bauxite entre {debut} et {fin} ?
WITH avant AS (
    SELECT pays, production_t FROM '{data}/bauxite_monde.csv' WHERE annee = {debut}
),
apres AS (
    SELECT pays, production_t FROM '{data}/bauxite_monde.csv' WHERE annee = {fin}
),
hausse AS (
    SELECT pays, (apres.production_t - avant.production_t) / 1e6 AS hausse_mt
    FROM avant JOIN apres USING (pays)
)
SELECT
    pays,
    hausse_mt,
    ROUND(100 * hausse_mt / (SELECT hausse_mt FROM hausse WHERE pays = 'Monde'), 0) AS part_de_la_hausse_pct
FROM hausse
ORDER BY hausse_mt DESC;
