-- Si Simandou montait en charge au même rythme que Roy Hill ou que S11D : volumes de 2026 à 2030.
WITH capacite AS (
    SELECT valeur AS capacite_mt
    FROM '{data}/simandou.csv'
    WHERE indicateur = 'capacite_totale'
),
rythme AS (
    SELECT
        annee_exploitation,
        MAX(production_mt / capacite_mt) FILTER (WHERE mine = 'Roy Hill') AS roy_hill,
        MAX(production_mt / capacite_mt) FILTER (WHERE mine = 'S11D')     AS s11d
    FROM '{data}/montee_en_charge_mines.csv'
    GROUP BY annee_exploitation
),
scenario AS (
    SELECT CAST(cle AS INTEGER) AS annee, valeur AS scenario_etape4
    FROM '{data}/hypotheses_simandou.csv'
    WHERE type = 'volume'
)
SELECT
    s.annee,
    s.scenario_etape4,
    ROUND(COALESCE(r.roy_hill, 1) * c.capacite_mt, 0) AS comme_roy_hill,   -- Roy Hill reste à 100 % après l'année 3
    ROUND(r.s11d * c.capacite_mt, 0) AS comme_s11d
FROM scenario s
JOIN rythme r ON r.annee_exploitation = s.annee - 2025
CROSS JOIN capacite c
ORDER BY s.annee;
