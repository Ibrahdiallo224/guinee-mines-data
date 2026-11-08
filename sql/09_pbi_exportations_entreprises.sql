-- Exportations de bauxite par entreprise et par année, en millions de tonnes (Ministère des Mines).
SELECT annee, entreprise, exportation_t / 1e6 AS exportation_mt
FROM '{data}/bauxite_par_entreprise.csv'
WHERE exportation_t IS NOT NULL
ORDER BY annee, exportation_mt DESC;
