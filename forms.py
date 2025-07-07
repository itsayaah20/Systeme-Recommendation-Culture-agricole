# AGROYA/agri_re/forms.py

from django import forms

class CultureRecommendationForm(forms.Form):
    REGION_CHOICES = [
        ("Meknès", "Meknès"),
        ("Fès", "Fès"),
        ("Tanger", "Tanger"),
        ("Agadir", "Agadir"),
        ("Ouarzazate", "Ouarzazate"),
        ("Rabat", "Rabat"),
        ("Casablanca", "Casablanca"),
    ]

    TYPE_SOL_CHOICES = [
        ("Argileux", "Argileux"),
        ("Sableux", "Sableux"),
        ("Limoneux", "Limoneux"),
        ("Calcaire", "Calcaire"),
        ("Humifère", "Humifère"),
    ]

    IRRIGATION_CHOICES = [
        ("Oui", "Oui"),
        ("Non", "Non"),
    ]

    PERIODE_PLANTATION_CHOICES = [
        ("Mars - Avril", "Mars - Avril"),
        ("Mai - Juin", "Mai - Juin"),
        ("Septembre - Octobre", "Septembre - Octobre"),
        ("Toute l’année", "Toute l’année"),
    ]

    SENSIBILITE_CHOICES = [
        ("Faible", "Faible"),
        ("Moyenne", "Moyenne"),
        ("Forte", "Forte"),
    ]

    # Champs
    region = forms.ChoiceField(
        choices=REGION_CHOICES,
        label="Région",
        required=True
    )
    type_sol = forms.ChoiceField(
        choices=TYPE_SOL_CHOICES,
        label="Type de sol",
        required=True
    )
    ph = forms.FloatField(
        label="pH du sol",
        min_value=0.0,
        max_value=14.0,
        required=True
    )
    pluviometrie = forms.FloatField(
        label="Pluviométrie (mm/an)",
        min_value=0.0,
        required=True
    )
    temperature = forms.FloatField(
        label="Température (°C)",
        min_value=-50.0,
        max_value=60.0,
        required=True
    )
    irrigation = forms.ChoiceField(
        choices=IRRIGATION_CHOICES,
        label="Irrigation",
        required=True
    )
    budget = forms.FloatField(
        label="Budget disponible (MAD/ha)",
        min_value=0.0,
        required=True
    )
    prix = forms.FloatField(
        label="Prix (MAD/kg)",
        min_value=0.0,
        required=True
    )
    rendement = forms.FloatField(
        label="Rendement (kg/ha)",
        min_value=0.0,
        required=True
    )
    periode_plantation = forms.ChoiceField(
        choices=PERIODE_PLANTATION_CHOICES,
        label="Période de plantation",
        required=True
    )
    duree_culture = forms.FloatField(
        label="Durée de culture (mois)",
        min_value=0.0,
        required=True
    )
    sensibilite_climat = forms.ChoiceField(
        choices=SENSIBILITE_CHOICES,
        label="Sensibilité au climat",
        required=True
    )
    benefice = forms.FloatField(
        label="Bénéfice estimé (MAD/ha)",
        min_value=0.0,
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        ph_val = cleaned_data.get("ph")
        if ph_val is not None and not (0.0 <= ph_val <= 14.0):
            self.add_error("ph", "Le pH doit être compris entre 0 et 14.")
        return cleaned_data

    def get_mapped_data(self):
        """
        Retourne un dict dont les clés correspondent EXACTEMENT
        aux colonnes que le modèle attend.
        """
        cleaned = self.cleaned_data
        return {
            "Région": cleaned["region"],
            "Type de sol": cleaned["type_sol"],
            "pH du sol": cleaned["ph"],
            "Pluviométrie (mm/an)": cleaned["pluviometrie"],
            "Température (°C)": cleaned["temperature"],
            "Irrigation": cleaned["irrigation"],
            "Budget disponible (MAD/ha)": cleaned["budget"],
            "Prix (MAD/kg)": cleaned["prix"],
            "Rendement (kg/ha)": cleaned["rendement"],
            "Période de plantation": cleaned["periode_plantation"],
            "Durée de culture (mois)": cleaned["duree_culture"],
            "Sensibilité au climat": cleaned["sensibilite_climat"],
            "Bénéfice estimé (MAD/ha)": cleaned["benefice"],
        }

from django import forms
from .models import SuiviCulture

class SuiviCultureForm(forms.ModelForm):
    class Meta:
        model = SuiviCulture
        fields = ['culture', 'date_semis']  # seulement les champs utiles pour l'utilisateur
        widgets = {
            'date_semis': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'culture': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'culture': 'Culture à suivre',
            'date_semis': 'Date de début de la culture',
        }

