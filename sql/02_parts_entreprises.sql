-- Part de chaque entreprise dans les exportations de bauxite d'une année, et part cumulée.
-- Les fonctions de fenêtre (OVER) calculent le total sans regrouper les lignes.
SELECT entreprise,
       exportation_t / 1e6 AS millions_tonnes,
       100 * exportation_t / SUM(exportation_t) OVER () AS part_pct,
       100 * SUM(exportation_t) OVER (ORDER BY exportation_t DESC)
           / SUM(exportation_t) OVER () AS part_cumulee_pct
FROM '{data}/bauxite_par_entreprise.csv'
WHERE annee = {annee}
ORDER BY exportation_t DESC;
