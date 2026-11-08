-- Production de bauxite par pays et par année, en millions de tonnes sèches (USGS), format long pour Power BI.
SELECT annee, pays, production_t / 1e6 AS production_mt
FROM '{data}/bauxite_monde.csv'
ORDER BY annee, pays;
