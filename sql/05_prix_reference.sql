-- Prix utilisés pour convertir les volumes prévus en dollars.
SELECT produit, prix, unite, source
FROM '{data}/prix_reference.csv';
