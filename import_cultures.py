# import_cultures.py

import os
import django
import pandas as pd

# Initialise Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AGROYA.settings")  # adapte si ton projet s'appelle autrement
django.setup()

from agri_re.models import Culture

# Charger le fichier
df = pd.read_excel("recommandations_enrichi.xlsx")

# Pour éviter les doublons
cultures_deja_importees = Culture.objects.values_list('nom_culture', flat=True)

for _, row in df.iterrows():
    nom = row['Culture recommandée']
    if nom not in cultures_deja_importees:
        Culture.objects.create(
            nom_culture=nom,
            type_sol=row.get('Type de sol', 'Sableux'),
            ph_min=row.get('pH du sol', 6.0),
            ph_max=row.get('pH du sol', 7.5),
            temperature_optimale=row.get('Température (°C)', 20),
            pluviometrie_min=row.get('Pluviométrie (mm/an)', 300),
            pluviometrie_max=row.get('Pluviométrie (mm/an)', 600),
            irrigation='oui' if row.get('Irrigation', '').lower() == 'oui' else 'non',
            budget_min=max(row.get('Budget disponible (MAD/ha)', 5000) - 3000, 1000),
            budget_max=row.get('Budget disponible (MAD/ha)', 15000),
        )
        print(f"✅ Ajouté : {nom}")

print("🎉 Importation terminée.")
