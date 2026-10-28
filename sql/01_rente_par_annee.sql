-- Rente minière par pays et par année, 2000-2021.
-- Les 0 de la Guinée à partir de 2019 sont des données manquantes : NULLIF les transforme en NULL.
SELECT pays, annee,
       CASE WHEN code_pays = 'GIN' AND annee >= 2019 THEN NULLIF(valeur, 0)
            ELSE valeur END AS valeur
FROM '{data}/rente_miniere.csv'
WHERE annee <= 2021;
