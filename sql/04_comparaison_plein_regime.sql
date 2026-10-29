-- Simandou à plein régime (120 Mt/an) comparé à la bauxite et au PIB de la Guinée en 2025.
-- UNION ALL empile des résultats venant de fichiers différents dans un seul tableau.
WITH capacite AS (
    SELECT valeur AS mt FROM '{data}/simandou.csv' WHERE indicateur = 'capacite_totale'
)
SELECT 'PIB de la Guinée (2025)' AS element,
       valeur / 1e9 AS milliards_usd
FROM '{data}/pib.csv'
WHERE code_pays = 'GIN' AND annee = 2025
UNION ALL
SELECT 'Bauxite achetée par le monde (2025)',
       SUM(valeur_usd) / 1e9
FROM '{data}/comtrade_miroir.csv'
WHERE produit = 'bauxite' AND annee = 2025
UNION ALL
SELECT 'Simandou à 120 Mt, prix ' || h.cle,
       c.mt * h.valeur / 1000
FROM '{data}/hypotheses_simandou.csv' h, capacite c
WHERE h.type = 'prix';
