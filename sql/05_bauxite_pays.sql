-- Production de bauxite par pays (millions de tonnes sèches, USGS), part de la Guinée et son rang mondial.
WITH par_pays AS (
    SELECT
        annee,
        SUM(production_t) FILTER (WHERE pays = 'Guinée')    / 1e6 AS guinee,
        SUM(production_t) FILTER (WHERE pays = 'Australie') / 1e6 AS australie,
        SUM(production_t) FILTER (WHERE pays = 'Chine')     / 1e6 AS chine,
        SUM(production_t) FILTER (WHERE pays = 'Monde')     / 1e6 AS monde
    FROM '{data}/bauxite_monde.csv'
    GROUP BY annee
)
SELECT
    annee,
    guinee,
    australie,
    chine,
    monde,
    ROUND(100 * guinee / monde, 1) AS part_guinee_pct,
    1 + (australie > guinee)::INT + (chine > guinee)::INT AS rang_guinee
FROM par_pays
ORDER BY annee;
