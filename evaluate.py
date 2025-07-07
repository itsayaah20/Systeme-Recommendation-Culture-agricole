import os
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
from django.conf import settings

# Chemins vers les fichiers modèle et encodeurs
MODEL_PATH = os.path.join(settings.BASE_DIR, "ml_models", "decision_tree_model.pkl")
ENCODERS_PATH = os.path.join(settings.BASE_DIR, "ml_models", "label_encoders.pkl")

# Chargement du modèle et des encodeurs
try:
    model = joblib.load(MODEL_PATH)
    label_encoders = joblib.load(ENCODERS_PATH)
    print(f"✅ Modèle chargé : {MODEL_PATH}")
    print(f"✅ Encodeurs chargés : {ENCODERS_PATH}")
except Exception as e:
    raise RuntimeError(f"❌ Erreur de chargement du modèle ou des encodeurs : {e}")

def evaluate_model(X_test, y_test):
    """
    Évalue la performance du modèle sur les données de test
    
    Args:
        X_test: données d'entrée de test
        y_test: labels de test
    
    Returns:
        dict: métriques de performance
    """
    # Prédictions
    y_pred = model.predict(X_test)
    
    # Calcul des métriques
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    # Conversion des labels numériques en labels de culture
    if "Culture recommandée" in label_encoders:
        y_test_labels = label_encoders["Culture recommandée"].inverse_transform(y_test)
        y_pred_labels = label_encoders["Culture recommandée"].inverse_transform(y_pred)
        
        # Rapport détaillé par culture
        detailed_report = classification_report(y_test_labels, y_pred_labels)
    else:
        detailed_report = "Encodeur de culture non disponible"
    
    return {
        'accuracy': accuracy,
        'classification_report': report,
        'confusion_matrix': cm,
        'detailed_report': detailed_report
    }

def print_evaluation_results(results):
    """Affiche les résultats de l'évaluation"""
    print("\n=== Résultats de l'évaluation du modèle ===")
    print(f"\nPrécision globale: {results['accuracy']:.2%}")
    print("\nRapport de classification:")
    print(results['classification_report'])
    print("\nMatrice de confusion:")
    print(results['confusion_matrix'])
    print("\nRapport détaillé par culture:")
    print(results['detailed_report'])
