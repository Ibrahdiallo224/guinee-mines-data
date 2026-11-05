import os
import urllib.request

# Rapports ITIE Guinée publiés sur eiti.org (le lien télécharge directement le PDF)
RAPPORTS = {
    2022: "https://eiti.org/document/24349",   # publié en décembre 2024
    2023: "https://eiti.org/document/25580",   # publié en décembre 2025
}


def telecharger_rapport(annee, url):
    """Télécharge le rapport ITIE d'une année et l'enregistre dans data/itie/."""
    os.makedirs("data/itie", exist_ok=True)
    chemin = f"data/itie/rapport_itie_{annee}.pdf"
    if os.path.exists(chemin):                        # déjà téléchargé : on ne recommence pas
        print(f"{chemin} existe déjà")
        return
    demande = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(demande) as reponse:
        contenu = reponse.read()
    with open(chemin, "wb") as f:                     # "wb" : on écrit des octets, pas du texte
        f.write(contenu)
    print(f"{chemin} : {len(contenu) / 1e6:.1f} Mo")


for annee, url in RAPPORTS.items():
    telecharger_rapport(annee, url)
