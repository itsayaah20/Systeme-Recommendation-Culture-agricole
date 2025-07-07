import joblib
import os
import numpy as np

MODEL_PATH = os.path.join("ml_models", "decision_tree_model.pkl")
ENCODERS_PATH = os.path.join("ml_models", "label_encoders.pkl")

def charger_modele_et_encoders():
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODERS_PATH)
    return model, encoders

def faire_prediction(donnees_dict):
    model, encoders = charger_modele_et_encoders()

    # Ordre exact des features
    features_order = [
        "Région", "Type de sol", "pH du sol", "Pluviométrie (mm/an)",
        "Température (°C)", "Irrigation", "Budget disponible (MAD/ha)",
        "Prix (MAD/kg)", "Rendement (kg/ha)", "Période de plantation",
        "Durée de culture (mois)", "Sensibilité au climat", "Bénéfice estimé (MAD/ha)"
    ]

    # Complétez les valeurs manquantes avec des valeurs par défaut
    data_complete = {
        "Prix (MAD/kg)": 10.0,
        "Rendement (kg/ha)": 5000,
        "Période de plantation": "mars",
        "Durée de culture (mois)": 4,
        "Sensibilité au climat": "moyenne",
        "Bénéfice estimé (MAD/ha)": 15000
    }
    data_complete.update(donnees_dict)

    # Encodage et construction du vecteur
    vecteur = []
    for f in features_order:
        val = data_complete[f]
        if f in encoders:
            val = encoders[f].transform([val])[0]
        vecteur.append(val)

    X_input = np.array([vecteur])
    prediction = model.predict(X_input)[0]

    culture_predite = encoders["Culture recommandée"].inverse_transform([prediction])[0]
    return culture_predite

def duree_saison_en_jours(nom_saison):
    durees = {
        'Printemps': 92,
        'Été': 93,
        'Automne': 91,
        'Hiver': 90  # on prend 90 pour simplifier
    }
    return durees.get(nom_saison, 90)  # valeur par défaut si saison inconnue