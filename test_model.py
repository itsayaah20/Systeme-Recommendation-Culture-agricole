from django.conf import settings
from .predict import faire_recommandation
from .forms import CultureRecommendationForm

# Créer des données de test qui correspondent au formulaire
test_data = {
    'region': 'Meknes',
    'type_sol': 'Argileux',
    'ph': 7.0,
    'pluviometrie': 450.0,
    'temperature': 22.0,
    'irrigation': 'oui',
    'budget': 15000.0,
    'prix': 10.0,
    'periode_plantation': 'printemps',
    'duree_culture': 6.0,
    'sensibilite_climat': 'moyenne'
}

# Créer une instance du formulaire avec les données de test
form = CultureRecommendationForm(test_data)

if form.is_valid():
    # Obtenir les données mappées pour le modèle
    mapped_data = form.get_mapped_data()
    print("\nDonnées mappées pour le modèle:", mapped_data)
    
    # Faire la recommandation
    try:
        result = faire_recommandation(mapped_data)
        print("\nRésultat de la recommandation:", result)
    except Exception as e:
        print(f"❌ Erreur lors de la recommandation: {e}")
else:
    print("❌ Le formulaire n'est pas valide:", form.errors)
