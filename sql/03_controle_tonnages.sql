-- Contrôle qualité : tonnages déclarés par les acheteurs comparés aux exportations publiées
-- par le Ministère des Mines. poids_estime = vrai quand le poids a été estimé par l'ONU.
WITH miroir AS (
    SELECT annee,
           SUM(poids_kg) / 1e9 AS miroir_mt,
           COUNT(*) FILTER (WHERE poids_estime) AS poids_estimes
    FROM '{data}/comtrade_miroir.csv'
    WHERE produit = 'bauxite'
    GROUP BY annee
),
ministere AS (
    SELECT annee, valeur / 1e6 AS ministere_mt
    FROM '{data}/sources_nationales.csv'
    WHERE indicateur = 'bauxite_exportation'
)
SELECT m.annee,
       ROUND(ministere_mt, 1) AS ministere_mt,
       ROUND(miroir_mt, 1) AS miroir_mt,
       ROUND(100 * miroir_mt / ministere_mt) AS couverture_pct,
       poids_estimes
FROM miroir m
JOIN ministere USING (annee)
ORDER BY m.annee;
