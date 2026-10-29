-- Une fois la montée en charge terminée (à partir de l'année 3), à quel % de sa capacité la mine tourne-t-elle ?
SELECT
    mine,
    COUNT(*) AS nb_annees,
    ROUND(100 * AVG(production_mt / capacite_mt), 0) AS moyenne_pct,
    ROUND(100 * MAX(production_mt / capacite_mt), 0) AS meilleure_annee_pct
FROM '{data}/montee_en_charge_mines.csv'
WHERE annee_exploitation >= 3
GROUP BY mine
ORDER BY mine;
