-- Ce que chaque société a payé à l'État en {annee} (montant confirmé par l'État après ajustements), en millions de dollars.
WITH paiements AS (
    SELECT s.nom_court, s.produit, p.etat_ajuste / t.gnf_par_usd / 1e6 AS millions_usd
    FROM '{data}/itie_paiements_par_societe.csv' p
    JOIN '{data}/itie_societes.csv' s ON p.nom = s.nom_itie
    JOIN '{data}/itie_taux_change.csv' t USING (annee)
    WHERE p.annee = {annee}
)
SELECT
    RANK() OVER (ORDER BY millions_usd DESC) AS rang,
    nom_court,
    produit,
    ROUND(millions_usd, 1) AS millions_usd,
    ROUND(100 * millions_usd / SUM(millions_usd) OVER (), 1) AS part_pct
FROM paiements
ORDER BY rang;
