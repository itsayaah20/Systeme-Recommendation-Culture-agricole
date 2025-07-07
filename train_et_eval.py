import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, f1_score
from xgboost import XGBClassifier

# 1) Chargement du dataset
csv_path = "C:\\Users\\lenovo\\Downloads\\final pfa\\AGROYA\\agri_dataset_synthetique_oriente.csv"
df = pd.read_csv(csv_path)

# 2) Séparation features / cible
X = df.drop("Culture recommandée", axis=1)
y = df["Culture recommandée"]

# 3) Split train / test AVANT encodage
X_train, X_test, y_train_text, y_test_text = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)

# 4) Encodage des colonnes catégorielles
label_encoders = {}
cat_cols = X_train.select_dtypes(include=["object"]).columns.tolist()

for col in cat_cols:
    le = LabelEncoder()
    X_train[col] = le.fit_transform(X_train[col].astype(str))
    X_test[col] = le.transform(X_test[col].astype(str))
    label_encoders[col] = le

# Encodage de la cible
le_target = LabelEncoder()
y_train = le_target.fit_transform(y_train_text.astype(str))
y_test = le_target.transform(y_test_text.astype(str))
label_encoders["Culture recommandée"] = le_target

# 5) GridSearchCV pour déterminer les meilleurs hyperparamètres
param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [4, 6, 8],
    "learning_rate": [0.05, 0.1, 0.2],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0]
}

xgb_base = XGBClassifier(
    objective="multi:softmax",
    num_class=len(le_target.classes_),
    eval_metric="mlogloss",
    random_state=42
)

clf = GridSearchCV(
    estimator=xgb_base,
    param_grid=param_grid,
    scoring="f1_macro",
    cv=3,
    n_jobs=-1,
    verbose=1
)

print("🔍 Lancement du GridSearchCV…")
clf.fit(X_train, y_train)

print("✅ Meilleurs paramètres trouvés :", clf.best_params_)
print(f"→ Meilleur score F1‐macro (CV) : {clf.best_score_:.4f}")

model = clf.best_estimator_

# 6) Évaluation sur le test
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average="macro")

print(f"\n✅ Accuracy TEST : {acc:.4f}")
print(f"🎯 F1-macro TEST : {f1:.4f}\n")
print("📊 Rapport de classification :")
print(classification_report(y_test, y_pred, target_names=le_target.classes_))

# 7) Sauvegarde du modèle et des encodeurs
model_dir = os.path.join(os.getcwd(), "ml_models")
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "xgboost_model_oriente.pkl")
encoders_path = os.path.join(model_dir, "label_encoders_oriente.pkl")

joblib.dump(model, model_path)
joblib.dump(label_encoders, encoders_path)

print(f"\n✅ Modèle sauvegardé dans : {model_path}")
print(f"✅ Encodeurs sauvegardés dans : {encoders_path}")
