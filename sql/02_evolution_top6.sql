-- Exportations par année des 6 premières entreprises de la dernière année
SELECT annee, entreprise, exportation_t / 1e6 AS millions_tonnes
FROM '{data}/bauxite_par_entreprise.csv'
WHERE entreprise IN (
    SELECT entreprise
    FROM '{data}/bauxite_par_entreprise.csv'
    WHERE annee = {annee}
    ORDER BY exportation_t DESC
    LIMIT 6
);
