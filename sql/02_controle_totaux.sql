-- Contrôle qualité : la somme des entreprises est-elle égale au total publié ?
SELECT b.annee,
       SUM(b.production_t)::BIGINT AS somme_entreprises,
       MAX(n.valeur)::BIGINT       AS total_publie,
       SUM(b.production_t)::BIGINT - MAX(n.valeur)::BIGINT AS ecart
FROM '{data}/bauxite_par_entreprise.csv' b
JOIN '{data}/sources_nationales.csv' n
  ON n.annee = b.annee AND n.indicateur = 'bauxite_production'
GROUP BY b.annee
ORDER BY b.annee;
