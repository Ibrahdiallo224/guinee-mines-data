-- Part de la bauxite, de l'or et de l'alumine dans la valeur des exportations (INS, 2020-2024).
-- Le CTE remet chaque produit en colonne (pivot) pour pouvoir diviser par le total.
WITH e AS (
    SELECT annee,
           SUM(valeur) FILTER (WHERE indicateur = 'export_total')   AS total,
           SUM(valeur) FILTER (WHERE indicateur = 'export_bauxite') AS bauxite,
           SUM(valeur) FILTER (WHERE indicateur = 'export_or')      AS orr,   -- OR est un mot réservé
           SUM(valeur) FILTER (WHERE indicateur = 'export_alumine') AS alumine
    FROM '{data}/sources_nationales.csv'
    WHERE unite = 'milliards GNF'
    GROUP BY annee
)
SELECT annee,
       ROUND(100 * bauxite / total, 1) AS bauxite_pct,
       ROUND(100 * orr / total, 1)     AS or_pct,
       ROUND(100 * alumine / total, 1) AS alumine_pct,
       ROUND(100 * (bauxite + orr + alumine) / total, 1) AS mines_pct
FROM e
ORDER BY annee;
