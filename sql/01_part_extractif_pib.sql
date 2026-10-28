-- Part des industries extractives dans le PIB, avec la source de chaque chiffre
SELECT annee, valeur AS part_extractif_pib_pct, source, note
FROM '{data}/sources_nationales.csv'
WHERE indicateur = 'part_extractif_pib'
ORDER BY annee;
