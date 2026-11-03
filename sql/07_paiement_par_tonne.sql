-- Bauxite : combien chaque société paie à l'État par tonne exportée, en 2022 et 2023 (dollars par tonne).
WITH paiements AS (
    SELECT p.annee, s.nom_court, p.etat_ajuste / t.gnf_par_usd AS usd
    FROM '{data}/itie_paiements_par_societe.csv' p
    JOIN '{data}/itie_societes.csv' s ON p.nom = s.nom_itie
    JOIN '{data}/itie_taux_change.csv' t USING (annee)
    WHERE s.produit = 'bauxite'
),
par_tonne AS (
    SELECT p.annee, p.nom_court, p.usd / b.exportation_t AS usd_par_tonne
    FROM paiements p
    JOIN '{data}/bauxite_par_entreprise.csv' b
      ON b.annee = p.annee AND b.entreprise = p.nom_court
    WHERE b.exportation_t > 0
)
SELECT
    nom_court,
    ROUND(MAX(usd_par_tonne) FILTER (WHERE annee = 2022), 2) AS usd_tonne_2022,
    ROUND(MAX(usd_par_tonne) FILTER (WHERE annee = 2023), 2) AS usd_tonne_2023
FROM par_tonne
GROUP BY nom_court
ORDER BY usd_tonne_2023 DESC NULLS LAST;
