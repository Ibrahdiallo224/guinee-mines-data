-- Évolution des paiements de chaque société entre 2022 et 2023 (millions de dollars, montants confirmés par l'État).
WITH paiements AS (
    SELECT p.annee, s.nom_court, p.etat_ajuste / t.gnf_par_usd / 1e6 AS millions_usd
    FROM '{data}/itie_paiements_par_societe.csv' p
    JOIN '{data}/itie_societes.csv' s ON p.nom = s.nom_itie
    JOIN '{data}/itie_taux_change.csv' t USING (annee)
),
cote_a_cote AS (
    SELECT nom_court,
           SUM(millions_usd) FILTER (WHERE annee = 2022) AS usd_2022,
           SUM(millions_usd) FILTER (WHERE annee = 2023) AS usd_2023
    FROM paiements
    GROUP BY nom_court
)
SELECT
    nom_court,
    ROUND(usd_2022, 1) AS usd_2022,
    ROUND(usd_2023, 1) AS usd_2023,
    ROUND(100 * (usd_2023 - usd_2022) / usd_2022, 0) AS variation_pct,
    CASE
        WHEN usd_2022 IS NULL THEN 'nouvelle en 2023'
        WHEN usd_2023 IS NULL THEN 'absente en 2023'
    END AS remarque
FROM cote_a_cote
ORDER BY COALESCE(usd_2023, 0) DESC;
