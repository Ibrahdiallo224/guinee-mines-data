-- Les hypothèses du scénario, avec leur justification.
SELECT type, cle, valeur, unite, justification
FROM '{data}/hypotheses_simandou.csv'
ORDER BY type DESC, cle;
