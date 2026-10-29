-- Taxe d'extraction que toucherait l'État sur le fer de Simandou à plein régime,
-- comparée à la taxe minière payée par les sociétés bauxitiques en 2024 (étape 2).
WITH taux AS (
    SELECT valeur / 100 AS taux FROM '{data}/hypotheses_simandou.csv' WHERE cle = 'extraction_fer'
),
capacite AS (
    SELECT valeur AS mt FROM '{data}/simandou.csv' WHERE indicateur = 'capacite_totale'
),
bauxite AS (
    SELECT SUM(taxe_miniere_usd) / 1e6 AS millions_usd
    FROM '{data}/taxes_bauxite_par_entreprise.csv'
    WHERE annee = 2024
)
SELECT h.cle AS scenario_prix,
       h.valeur AS usd_par_tonne,
       h.valeur * t.taux AS taxe_usd_par_tonne,
       c.mt * h.valeur * t.taux AS taxe_fer_millions_usd,
       b.millions_usd AS taxe_bauxite_2024_millions_usd
FROM '{data}/hypotheses_simandou.csv' h, taux t, capacite c, bauxite b
WHERE h.type = 'prix'
ORDER BY h.valeur;
