-- Paiements à l'État par produit (bauxite, or, fer, alumine), 2022 et 2023, en millions de dollars.
WITH paiements AS (
    SELECT p.annee, s.produit, p.etat_ajuste / t.gnf_par_usd / 1e6 AS millions_usd
    FROM '{data}/itie_paiements_par_societe.csv' p
    JOIN '{data}/itie_societes.csv' s ON p.nom = s.nom_itie
    JOIN '{data}/itie_taux_change.csv' t USING (annee)
)
SELECT
    produit,
    ROUND(SUM(millions_usd) FILTER (WHERE annee = 2022), 1) AS usd_2022,
    ROUND(SUM(millions_usd) FILTER (WHERE annee = 2023), 1) AS usd_2023,
    ROUND(100 * SUM(millions_usd) FILTER (WHERE annee = 2023)
              / SUM(SUM(millions_usd) FILTER (WHERE annee = 2023)) OVER (), 1) AS part_2023_pct
FROM paiements
GROUP BY produit
ORDER BY usd_2023 DESC;
