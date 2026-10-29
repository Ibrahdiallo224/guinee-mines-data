-- Classement mondial du minerai de fer (2025), en ajoutant la Guinée avec Simandou à plein régime.
WITH pays AS (
    SELECT pays, production_t / 1e6 AS production_mt
    FROM '{data}/fer_monde.csv'
    WHERE pays NOT IN ('Monde', 'Autres pays')
    UNION ALL
    SELECT 'Guinée (Simandou)', valeur
    FROM '{data}/simandou.csv'
    WHERE indicateur = 'capacite_totale'
),
monde AS (
    SELECT production_t / 1e6 AS monde_mt
    FROM '{data}/fer_monde.csv'
    WHERE pays = 'Monde'
)
SELECT
    RANK() OVER (ORDER BY production_mt DESC) AS rang,
    pays,
    production_mt,
    ROUND(100 * production_mt / monde_mt, 1) AS part_monde_pct
FROM pays
CROSS JOIN monde
ORDER BY rang;
