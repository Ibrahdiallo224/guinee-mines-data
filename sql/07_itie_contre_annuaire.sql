-- Contrôle croisé 2023 : les paiements ITIE comparés aux taxes publiées par le ministère des Mines (annuaire 2023).
WITH itie AS (
    SELECT s.nom_court,
           p.societe_ajuste / t.gnf_par_usd / 1e6 AS itie_societe,
           p.etat_ajuste    / t.gnf_par_usd / 1e6 AS itie_etat
    FROM '{data}/itie_paiements_par_societe.csv' p
    JOIN '{data}/itie_societes.csv' s ON p.nom = s.nom_itie
    JOIN '{data}/itie_taux_change.csv' t USING (annee)
    WHERE p.annee = 2023
),
ministere AS (
    SELECT entreprise AS nom_court,
           (COALESCE(taxe_miniere_usd, 0) + COALESCE(droits_douane_usd, 0)
            + COALESCE(contribution_communautaire_usd, 0)) / 1e6 AS ministere
    FROM '{data}/taxes_bauxite_par_entreprise.csv'
    WHERE annee = 2023
)
SELECT
    nom_court,
    ROUND(m.ministere, 1) AS annuaire_mines_musd,
    ROUND(i.itie_etat, 1) AS itie_selon_etat_musd,
    ROUND(i.itie_societe, 1) AS itie_selon_societe_musd,
    CASE
        WHEN i.itie_etat < m.ministere THEN 'incohérent : l''ITIE (tous impôts) est plus bas que 3 taxes du ministère'
        ELSE 'cohérent : l''ITIE couvre plus d''impôts'
    END AS constat
FROM ministere m
JOIN itie i USING (nom_court)
ORDER BY m.ministere DESC;
