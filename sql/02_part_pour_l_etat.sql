-- Paiements des sociétés bauxitiques à l'État, comparés à la valeur des exportations de bauxite.
-- La valeur INS est en milliards de francs guinéens : conversion en dollars avec le taux BCRG.
WITH recettes AS (
    SELECT SUM(taxe_miniere_usd) + SUM(droits_douane_usd)
           + SUM(contribution_communautaire_usd) AS total_usd
    FROM '{data}/taxes_bauxite_par_entreprise.csv'
    WHERE annee = {annee}
),
exportations AS (
    SELECT valeur * 1e9 / {taux_usd_gnf} AS valeur_usd
    FROM '{data}/sources_nationales.csv'
    WHERE indicateur = 'export_bauxite' AND annee = {annee}
)
SELECT ROUND(r.total_usd / 1e6)                   AS recettes_bauxite_millions_usd,
       ROUND(e.valeur_usd / 1e9, 2)               AS exportations_bauxite_milliards_usd,
       ROUND(100 * r.total_usd / e.valeur_usd, 1) AS part_pour_l_etat_pct
FROM recettes r, exportations e;
