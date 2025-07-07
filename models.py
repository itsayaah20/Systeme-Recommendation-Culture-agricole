from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings


# ================================
# === UTILISATEUR PERSONNALISÉ ===
# ================================

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, cne, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est requis")
        email = self.normalize_email(email)
        user = self.model(email=email, cne=cne, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, cne, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')

        return self.create_user(email, cne, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    cne = models.CharField(max_length=20, unique=True)
    nom_complet = models.CharField(max_length=100, blank=True, null=True)
    genre = models.CharField(max_length=10, blank=True, null=True)
    region = models.CharField(max_length=100)
    telephone = models.CharField(max_length=10)

    TYPE_AGRICULTURE_CHOICES = [
        ('élevage', 'Élevage'),
        ('culture', 'Culture'),
        ('mixte', 'Mixte')
    ]
    type_agriculture = models.CharField(max_length=10, choices=TYPE_AGRICULTURE_CHOICES)
    date_inscription = models.DateTimeField(default=timezone.now)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['cne']

    objects = UtilisateurManager()

    def __str__(self):
        return self.nom_complet or self.email


# =====================
# === AUTRES MODÈLES ==
# =====================
class Culture(models.Model):
    CATEGORIE_CHOICES = [
        ('Légume', 'Légume'),
        ('Fruit', 'Fruit'),
        ('Céréale', 'Céréale'),
    ]

    nom_culture = models.CharField(max_length=100, unique=True)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default='Légume')
    image = models.ImageField(upload_to='cultures/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type_sol = models.CharField(max_length=100)
    ph_min = models.FloatField()
    ph_max = models.FloatField()
    temperature_optimale = models.FloatField()
    pluviometrie_min = models.FloatField()
    pluviometrie_max = models.FloatField()
    irrigation = models.CharField(max_length=50, choices=[('oui', 'Oui'), ('non', 'Non')])
    budget_min = models.FloatField()
    budget_max = models.FloatField()
    saisons = models.CharField(max_length=200, null=True, blank=True)
    benefices = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.nom_culture

class Recommandation(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    date_recommandation = models.DateTimeField(auto_now_add=True)
    recommandations_generales = models.TextField()
    meteo = models.ForeignKey('Meteo',  on_delete=models.CASCADE, null=True, blank=True)
    recommandations_generales = models.TextField()
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('annulée', 'Annulée'),
    ]
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='active')
    date_annulation = models.DateTimeField(null=True, blank=True)



    def __str__(self):
        return f"Recommandation pour {self.utilisateur.nom_complet or self.utilisateur.email}"

class Meteo(models.Model):
    region = models.CharField(max_length=100)
    temperature_min = models.FloatField()
    temperature_max = models.FloatField()
    humidite_min = models.FloatField()
    humidite_max = models.FloatField()
    precipitation = models.FloatField()
    date_rapport = models.DateField()

    def __str__(self):
        return f"Météo pour {self.region} le {self.date_rapport}"

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WebPushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.TextField()
    auth_key = models.CharField(max_length=255)
    p256dh_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class SuiviCulture(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    date_semis = models.DateField()
    date_prochain_arrosage = models.DateField(null=True, blank=True)
    date_recolte_prevue = models.DateField(null=True, blank=True)
    rappel_arrosage = models.BooleanField(default=True)
    rappel_recolte = models.BooleanField(default=True)
    notes = models.TextField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=[
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ], default='en_cours')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suivi {self.culture.nom_culture} pour {self.utilisateur.nom_complet}"
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatbotMessage(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_ia"
    )
    question = models.TextField()
    reponse = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur.email} - {self.date.strftime('%Y-%m-%d %H:%M:%S')}"
