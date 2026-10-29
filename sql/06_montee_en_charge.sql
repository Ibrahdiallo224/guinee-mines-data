-- Montée en charge : production de chaque mine en % de sa capacité, année après année.
-- Roy Hill et S11D : chiffres réels. Simandou : le scénario de l'étape 4 (2026 = année 1).
WITH analogues AS (
    SELECT mine, annee_exploitation, production_mt, capacite_mt
    FROM '{data}/montee_en_charge_mines.csv'
),
simandou AS (
    SELECT
        'Simandou (scénario)' AS mine,
        CAST(cle AS INTEGER) - 2025 AS annee_exploitation,
        valeur AS production_mt,
        (SELECT valeur FROM '{data}/simandou.csv' WHERE indicateur = 'capacite_totale') AS capacite_mt
    FROM '{data}/hypotheses_simandou.csv'
    WHERE type = 'volume'
)
SELECT
    mine,
    annee_exploitation,
    production_mt,
    capacite_mt,
    ROUND(100 * production_mt / capacite_mt, 0) AS pct_capacite
FROM (SELECT * FROM analogues UNION ALL SELECT * FROM simandou)
ORDER BY mine, annee_exploitation;
