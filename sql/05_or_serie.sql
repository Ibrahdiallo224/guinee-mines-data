-- Production d'or industriel de 2008 à 2024, en tonnes. Avant 2008, l'USGS incluait l'orpaillage :
-- la série ne serait pas comparable, on commence donc en 2008.
SELECT annee, production_kg / 1000 AS valeur
FROM '{data}/or_production_longue.csv'
ORDER BY annee;
