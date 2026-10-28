-- Exportations de bauxite de la Guinée, en millions de tonnes (2019-2025)
SELECT annee, valeur / 1e6 AS millions_tonnes
FROM '{data}/sources_nationales.csv'
WHERE indicateur = 'bauxite_exportation'
ORDER BY annee;
