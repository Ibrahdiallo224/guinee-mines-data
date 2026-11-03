-- Ce que la société dit avoir payé, comparé à ce que l'État dit avoir reçu ({annee}, après ajustements).
WITH declarations AS (
    SELECT s.nom_court,
           p.societe_ajuste / t.gnf_par_usd / 1e6 AS selon_societe,
           p.etat_ajuste    / t.gnf_par_usd / 1e6 AS selon_etat
    FROM '{data}/itie_paiements_par_societe.csv' p
    JOIN '{data}/itie_societes.csv' s ON p.nom = s.nom_itie
    JOIN '{data}/itie_taux_change.csv' t USING (annee)
    WHERE p.annee = {annee}
)
SELECT
    nom_court,
    ROUND(selon_societe, 1) AS selon_societe_musd,
    ROUND(selon_etat, 1) AS selon_etat_musd,
    ROUND(selon_societe - selon_etat, 1) AS ecart_musd,
    CASE
        WHEN selon_societe = 0 THEN 'aucune déclaration de la société'
        WHEN ABS(selon_societe - selon_etat) <= 0.05 * selon_etat THEN 'concordant (moins de 5 %)'
        WHEN selon_societe > selon_etat THEN 'la société déclare plus'
        ELSE 'l''État déclare plus'
    END AS constat
FROM declarations
ORDER BY ABS(selon_societe - selon_etat) DESC;
