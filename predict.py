# agri_re/predict.py

import os
import joblib
from django.conf import settings
from .models import Culture

# On ne charge plus le modèle/encodeurs au niveau module.
# Ils seront chargés dynamiquement dans la fonction faire_recommandation().


# On s’attend exactement à ces 13 clés
feature_names = [
    "Région",
    "Type de sol",
    "pH du sol",
    "Pluviométrie (mm/an)",
    "Température (°C)",
    "Irrigation",
    "Budget disponible (MAD/ha)",
    "Prix (MAD/kg)",
    "Rendement (kg/ha)",
    "Période de plantation",
    "Durée de culture (mois)",
    "Sensibilité au climat",
    "Bénéfice estimé (MAD/ha)"
]

def faire_recommandation(mapped_data):
    """
    mapped_data doit contenir exactement les 13 clés ci‐dessus.
    Ex :
    mapped_data = {
      "Région": "Meknès",
      "Type de sol": "Limoneux",
      "pH du sol": 7.0,
      "Pluviométrie (mm/an)": 500.0,
      "Température (°C)": 22.0,
      "Irrigation": "Oui",
      "Budget disponible (MAD/ha)": 15000.0,
      "Prix (MAD/kg)": 8.0,
      "Rendement (kg/ha)": 20000.0,
      "Période de plantation": "Mars - Avril",
      "Durée de culture (mois)": 4.0,
      "Sensibilité au climat": "Moyenne",
      "Bénéfice estimé (MAD/ha)": 90000.0
    }
    """

    # 1) Construire les chemins vers les fichiers pickle "orientés"
    base_dir      = settings.BASE_DIR  # racine du projet
    model_path    = os.path.join(base_dir, "ml_models", "xgboost_model_oriente.pkl")
    encoders_path = os.path.join(base_dir, "ml_models", "label_encoders_oriente.pkl")

    # 2) Charger dynamiquement le modèle et les encodeurs
    try:
        model = joblib.load(model_path)
        label_encoders = joblib.load(encoders_path)
    except Exception as e:
        raise RuntimeError(f"❌ Erreur de chargement du modèle/encodeurs : {e}")

    # 3) Construire le vecteur d’entrée après encodage
    input_vector = []
    for feature in feature_names:
        val = mapped_data.get(feature)
        if val is None:
            return {"erreur": f"Donnée manquante pour '{feature}'"}

        # Si un LabelEncoder existe pour cette feature, transformer
        if feature in label_encoders:
            try:
                val = label_encoders[feature].transform([val])[0]
            except Exception:
                bonnes_valeurs = list(label_encoders[feature].classes_)
                return {
                    "erreur": (
                        f"Valeur inconnue pour '{feature}' → '{val}'.\n"
                        f"Valeurs autorisées : {bonnes_valeurs}"
                    )
                }
        input_vector.append(val)

    # 4) Prédiction
    try:
        pred_code = model.predict([input_vector])[0]
    except Exception as e:
        return {"erreur": f"Erreur lors de model.predict : {e}"}

    # 5) Décoder la classe en texte
    try:
        nom_culture = label_encoders["Culture recommandée"].inverse_transform([pred_code])[0]
    except Exception as e:
        return {"erreur": f"Impossible de décoder la prédiction : {e}"}

    # 6) Récupérer les infos de la culture depuis la base de données
    try:
        culture = Culture.objects.get(nom_culture__iexact=nom_culture)
    except Culture.DoesNotExist:
        return {"erreur": f"La culture '{nom_culture}' n'existe pas en base de données."}

    # 7) Construire un texte de recommandation détaillé
    text = (
        f"🌱 Recommandation : {culture.nom_culture}\n\n"
        f"✅ Région : {mapped_data.get('Région')}\n"
        f"✅ Type de sol : {culture.type_sol} (pH idéal : {culture.ph_min}–{culture.ph_max})\n"
        f"✅ Température optimale : {culture.temperature_optimale}°C\n"
        f"✅ Pluviométrie : {culture.pluviometrie_min}–{culture.pluviometrie_max} mm/an\n"
        f"✅ Budget recommandé : {culture.budget_min}–{culture.budget_max} MAD/ha\n"
        f"✅ Irrigation : {'Oui' if culture.irrigation.lower() == 'oui' else 'Non'}\n"
        f"✅ Périodes : {culture.saisons if culture.saisons else 'Toute l’année'}\n"
        f"✅ Bénéfices estimés : {culture.benefices if culture.benefices else 'Adaptée, résiliente'}"
    )

    # 8) Cultures complémentaires (exemple)
    recos = [{"nom_culture": culture.nom_culture, "description": text}]
    if culture.nom_culture.lower() == "blé":
        recos += [
            {"nom_culture": "Lentilles", "description": "Améliore la terre, bon compagnon du blé."},
            {"nom_culture": "Orge",     "description": "Bonne tolérance à la sécheresse."}
        ]
    elif culture.nom_culture.lower() == "tomate":
        recos += [
            {"nom_culture": "Poivron",   "description": "Même climat, bon compagnon de la tomate."},
            {"nom_culture": "Concombre", "description": "Rotation bonne pour le sol."}
        ]

    return {
        "texte": text,
        "recommendations": recos
    }
