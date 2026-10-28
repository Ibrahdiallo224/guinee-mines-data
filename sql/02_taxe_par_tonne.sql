-- Taxe minière payée par tonne exportée, pour les entreprises qui en déclarent une
SELECT t.entreprise, t.taxe_miniere_usd, b.exportation_t,
       t.taxe_miniere_usd / b.exportation_t AS usd_par_tonne
FROM '{data}/taxes_bauxite_par_entreprise.csv' t
JOIN '{data}/bauxite_par_entreprise.csv' b USING (annee, entreprise)
WHERE t.annee = {annee} AND t.taxe_miniere_usd IS NOT NULL;
