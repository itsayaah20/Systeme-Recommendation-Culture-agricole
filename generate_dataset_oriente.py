import pandas as pd
import numpy as np

# Définition des plages « typiques » pour chaque culture
cultures = {
    "Blé":       {"pH": (6.0, 7.0),  "pluie": (400, 600),  "temp": (18, 22)},
    "Orge":      {"pH": (6.5, 7.5),  "pluie": (300, 500),  "temp": (16, 20)},
    "Maïs":      {"pH": (5.5, 6.5),  "pluie": (500, 700),  "temp": (20, 26)},
    "Tomate":    {"pH": (5.5, 6.5),  "pluie": (300, 500),  "temp": (18, 28)},
    "Pomme de terre": {"pH": (5.0, 6.0), "pluie": (600, 800), "temp": (15, 20)},
    "Carotte":   {"pH": (6.0, 7.0),  "pluie": (400, 600),  "temp": (15, 20)},
    "Lentilles": {"pH": (6.0, 7.0),  "pluie": (300, 500),  "temp": (15, 20)},
    "Pastèque":  {"pH": (6.0, 7.0),  "pluie": (200, 400),  "temp": (22, 30)},
}

regions = ["Meknès","Fès","Agadir","Ouarzazate","Rabat"]
types_sol = ["Argileux","Sableux","Limoneux"]
irrigation = ["Oui","Non"]
periodes = ["Mars - Avril","Mai - Juin","Septembre - Octobre","Toute l’année"]
sensibilites = ["Faible","Moyenne","Forte"]

n_par_culture = 125  # 8×125 = 1000 lignes au total

data = []
for culture, specs in cultures.items():
    for _ in range(n_par_culture):
        ph = np.round(np.random.uniform(*specs["pH"]), 2)
        pluie = np.round(np.random.uniform(*specs["pluie"]), 1)
        temp = np.round(np.random.uniform(*specs["temp"]), 1)
        row = {
            "Région":        np.random.choice(regions),
            "Type de sol":   np.random.choice(types_sol),
            "pH du sol":     ph,
            "Pluviométrie (mm/an)": pluie,
            "Température (°C)":     temp,
            "Irrigation":    np.random.choice(irrigation),
            "Budget disponible (MAD/ha)": np.round(np.random.normal(18000, 4000), 2),
            "Prix (MAD/kg)": np.round(np.random.normal(8, 2), 2),
            "Rendement (kg/ha)": np.round(np.random.normal(18000, 3000), 2),
            "Période de plantation": np.random.choice(periodes),
            "Durée de culture (mois)": np.round(np.random.uniform(3, 6), 1),
            "Sensibilité au climat": np.random.choice(sensibilites),
            "Bénéfice estimé (MAD/ha)": None,  # calculé après
            "Culture recommandée": culture
        }
        # Calcul du bénéfice estimé
        row["Bénéfice estimé (MAD/ha)"] = np.round(
            row["Prix (MAD/kg)"] * row["Rendement (kg/ha)"] * 0.7, 2
        )
        data.append(row)

df_oriente = pd.DataFrame(data)
# Sauvegarde au format CSV à l’emplacement souhaité
df_oriente.to_csv("C:/Users/pc/AGROYA/agri_dataset_synthetique_oriente.csv", index=False)
print("✅ Dataset synthétique orienté généré dans : C:/Users/pc/AGROYA/agri_dataset_synthetique_oriente.csv")
