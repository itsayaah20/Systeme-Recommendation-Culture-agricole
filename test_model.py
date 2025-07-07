import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# -----------------------------
# 1. Construire les chemins vers le modèle et les encodeurs “orientés”
# -----------------------------
base_dir      = os.getcwd()  # racine du projet (où se trouve manage.py)
model_path    = os.path.join(base_dir, "ml_models", "xgboost_model_oriente.pkl")
encoders_path = os.path.join(base_dir, "ml_models", "label_encoders_oriente.pkl")

# -----------------------------
# 2. Charger le modèle et les encodeurs
# -----------------------------
model    = joblib.load(model_path)
encoders = joblib.load(encoders_path)

# -----------------------------
# 3. Charger le dataset synthétique orienté
# -----------------------------
csv_path   = os.path.join(base_dir, "agri_dataset_synthetique_oriente.csv")
df         = pd.read_csv(csv_path)
target_col = "Culture recommandée"

# -----------------------------
# 4. Séparer features / target
# -----------------------------
features = [
    "Région", "Type de sol", "pH du sol", "Pluviométrie (mm/an)", "Température (°C)",
    "Irrigation", "Budget disponible (MAD/ha)", "Prix (MAD/kg)", "Rendement (kg/ha)",
    "Période de plantation", "Durée de culture (mois)", "Sensibilité au climat",
    "Bénéfice estimé (MAD/ha)"
]
X_true_text  = df[features].copy()
y_true_text  = df[target_col].copy()

# -----------------------------
# 5. Encoder les features avec les mêmes LabelEncoder que pour l'entraînement
# -----------------------------
for col, le in encoders.items():
    if col == "Culture recommandée":
        continue
    if col in X_true_text.columns:
        valeurs_connues = set(le.classes_)
        # Filtrer les lignes dont la valeur est inconnue
        valeurs_données = set(X_true_text[col].astype(str).unique())
        inconnues = valeurs_données - valeurs_connues
        if inconnues:
            print(f"⚠️ Valeurs inconnues ignorées dans '{col}' : {inconnues}")
            mask = X_true_text[col].astype(str).isin(valeurs_connues)
            X_true_text = X_true_text[mask].reset_index(drop=True)
            y_true_text = y_true_text[mask].reset_index(drop=True)
        X_true_text[col] = le.transform(X_true_text[col].astype(str))

# -----------------------------
# 6. Encoder la cible
# -----------------------------
le_target = encoders["Culture recommandée"]
y_true = le_target.transform(y_true_text.astype(str))

# -----------------------------
# 7. Split en train/test pour évaluation
# -----------------------------
_, X_test, _, y_test = train_test_split(
    X_true_text, y_true, test_size=0.20, stratify=y_true, random_state=42
)

# -----------------------------
# 8. Prédictions sur X_test
# -----------------------------
y_pred = model.predict(X_test)

# -----------------------------
# 9. Calcul des métriques
# -----------------------------
acc = accuracy_score(y_test, y_pred)
print(f"\n✅ Accuracy sur le set de test synthétique orienté : {acc:.4f}")
print("📊 Rapport de classification :")
print(classification_report(
    y_test,
    y_pred,
    target_names=le_target.classes_
))

# -----------------------------
# 10. Quelques exemples décodés
# -----------------------------
print("\n🔍 Exemples (vrai vs prédit) :")
for i in range(min(10, len(y_test))):
    vrai   = le_target.inverse_transform([y_test[i]])[0]
    predit = le_target.inverse_transform([y_pred[i]])[0]
    print(f"🔹 Vrai : {vrai} | Prédit : {predit}")
