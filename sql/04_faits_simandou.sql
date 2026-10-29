-- Les chiffres clés de Simandou, tels que publiés (une ligne = un fait, avec sa source).
SELECT date, indicateur, valeur, unite, source
FROM '{data}/simandou.csv'
WHERE indicateur IN ('capacite_totale', 'capacite_simfer', 'capacite_wcs', 'investissement_simfer',
                     'part_etat_simfer', 'part_etat_rail_port', 'objectif_60mt_simfer',
                     'ventes_prevues_2026_min', 'ventes_prevues_2026_max', 'ventes_simfer_jan_sep_2026')
ORDER BY date;
