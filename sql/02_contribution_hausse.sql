-- Contribution de chaque entreprise à la hausse des exportations entre deux années
WITH v AS (
    SELECT entreprise,
           COALESCE(SUM(exportation_t) FILTER (WHERE annee = {debut}), 0) AS t_debut,
           COALESCE(SUM(exportation_t) FILTER (WHERE annee = {fin}), 0)   AS t_fin
    FROM '{data}/bauxite_par_entreprise.csv'
    GROUP BY entreprise
)
SELECT entreprise,
       ROUND((t_fin - t_debut) / 1e6, 1) AS hausse_mt,
       ROUND(100 * (t_fin - t_debut) / SUM(t_fin - t_debut) OVER (), 1) AS part_de_la_hausse_pct
FROM v
ORDER BY hausse_mt DESC
LIMIT 6;
