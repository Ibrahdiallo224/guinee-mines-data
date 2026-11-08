-- Paiements des sociétés minières à l'État (rapports ITIE), en millions de dollars, montants après ajustements
-- (les mêmes qu'à l'étape 7) : ce que la société déclare avoir payé, ce que l'État déclare avoir reçu, et l'écart.
SELECT
    p.annee,
    s.nom_court AS societe,
    s.produit,
    p.societe_ajuste / t.gnf_par_usd / 1e6 AS paye_selon_societe_musd,
    p.etat_ajuste / t.gnf_par_usd / 1e6 AS recu_selon_etat_musd,
    (p.societe_ajuste - p.etat_ajuste) / t.gnf_par_usd / 1e6 AS ecart_musd
FROM '{data}/itie_paiements_par_societe.csv' AS p
JOIN '{data}/itie_societes.csv' AS s ON s.nom_itie = p.nom
JOIN '{data}/itie_taux_change.csv' AS t ON t.annee = p.annee
ORDER BY p.annee, recu_selon_etat_musd DESC;
