# AGROYA/agri_re/views.py

import os
import joblib
import json
import numpy as np

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .forms import CultureRecommendationForm
from .models import Utilisateur, Recommandation, Culture
from .predict import faire_recommandation


# ------------------------------------------------------------------------
# Fonctions utilitaires pour mapper les valeurs du formulaire
# ------------------------------------------------------------------------

def map_season_to_planting_period(user_input):
    """
    Convertit le choix “printemps/été/automne/hiver” du formulaire
    en l’un des intervalles mensuels attendus par le modèle.
    """
    txt = user_input.lower()
    if txt == 'automne':
        return 'Septembre - Octobre'
    if txt == 'été':
        return 'Avril - Mai'
    if txt == 'printemps':
        return 'Mars - Avril'
    if txt == 'hiver':
        return 'Janvier - Février'

    # Si l’utilisateur a saisi directement un intervalle valide,
    # renvoyer tel quel.
    allowed = [
        'Avril - Mai', 'Janvier - Février', 'Mars - Avril',
        'Novembre - Décembre', 'Octobre - Novembre', 'Septembre - Octobre'
    ]
    return user_input if user_input in allowed else None


def _map_climat(value):
    """
    Convertit la chaîne du formulaire en l’une des valeurs exactes de l’encodeur.
    Par exemple 'Moyenne' → 'Modérée'; 'faible' → 'Faible', etc.
    """
    if not value:
        return None

    txt = value.strip().lower()
    if txt == 'moyenne':
        return 'Modérée'
    # Capitaliser pour correspondre exactement : 'faible' → 'Faible', 'élevée' → 'Élevée'
    return txt.capitalize()

from django.shortcuts import render

def page_accueil(request):
    return render(request, 'accueil.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def profil_utilisateur(request):
    return render(request, 'profil_utilisateur.html', {'user': request.user})

# ------------------------------------------------------------------------
# 1) HOME / ABOUT / CONTACT / SERVICES / RECHERCHE
# ------------------------------------------------------------------------

def home_view(request):
    return render(request, "home.html", {
        "vapid_key": settings.WEBPUSH_SETTINGS["VAPID_PUBLIC_KEY"]
    })


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def services(request):
    return render(request, 'services.html')


def recherche(request):
    query = request.GET.get('q', '').strip()
    resultats = []
    if query:
        resultats = Culture.objects.filter(nom_culture__icontains=query)
    return render(request, 'resultats_recherche.html', {
        'resultats': resultats,
        'query': query
    })


# ------------------------------------------------------------------------
# 2) DASHBOARD
# ------------------------------------------------------------------------

@login_required(login_url='login')
def dashboard(request):
    query = request.GET.get('q', '').strip()
    cultures = Culture.objects.all()
    if query:
        cultures = cultures.filter(nom_culture__icontains=query)

    latitude = request.session.get('latitude')
    longitude = request.session.get('longitude')

    recommandations = Recommandation.objects.filter(utilisateur=request.user, statut='active').order_by('-date_creation')[:5]
    # On récupère les suivis
    suivis = SuiviCulture.objects.filter(utilisateur=request.user).order_by('-date_creation')

    context = {
        'cultures': cultures,
        'query': query,
        'latitude': latitude,
        'longitude': longitude,
        'recommandations': recommandations,
        'suivis': suivis,
        'vapid_key': settings.WEBPUSH_SETTINGS["VAPID_PUBLIC_KEY"]
    }
    return render(request, 'dashboard.html', context)


# ------------------------------------------------------------------------
# 3) SIGNUP
# ------------------------------------------------------------------------

def signup(request):
    if request.method == 'POST':
        cne = request.POST.get('cne', '').strip()
        nom_complet = request.POST.get('nom_complet', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        region = request.POST.get('region', '').strip()
        type_agriculture = request.POST.get('type_agriculture', '').strip()
        genre = request.POST.get('genre', '').strip()
        mot_de_passe = request.POST.get('mot_de_passe', '')

        if Utilisateur.objects.filter(cne=cne).exists():
            return render(request, 'signup.html', {'message': 'Ce CNE existe déjà.'})

        if email and Utilisateur.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'message': 'Cet email est déjà utilisé.'})

        utilisateur = Utilisateur(
            cne=cne,
            nom_complet=nom_complet,
            email=email,
            region=region,
            telephone=telephone,
            type_agriculture=type_agriculture,
            genre=genre
        )
        utilisateur.set_password(mot_de_passe)
        utilisateur.save()
        return redirect('login')

    return render(request, 'signup.html')


# ------------------------------------------------------------------------
# 4) LOGIN / LOGOUT
# ------------------------------------------------------------------------
# AGROYA/agri_re/views.py
def base_page(request):
    return render(request, "base.html")

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Utilisateur

# INSCRIPTION
def signup(request):
    if request.method == 'POST':
        cne = request.POST.get('cne', '').strip()
        nom_complet = request.POST.get('nom_complet', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        region = request.POST.get('region', '').strip()
        type_agriculture = request.POST.get('type_agriculture', '').strip()
        genre = request.POST.get('genre', '').strip()
        mot_de_passe = request.POST.get('mot_de_passe', '')

        if Utilisateur.objects.filter(cne=cne).exists():
            return render(request, 'signup.html', {'message': 'Ce CNE existe déjà.'})

        if email and Utilisateur.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'message': 'Cet email est déjà utilisé.'})

        utilisateur = Utilisateur(
            cne=cne,
            nom_complet=nom_complet,
            email=email,
            region=region,
            telephone=telephone,
            type_agriculture=type_agriculture,
            genre=genre
        )
        utilisateur.set_password(mot_de_passe)
        utilisateur.save()
        return redirect('login')

    return render(request, 'signup.html')


# CONNEXION
def login_view(request):
    message = ''
    if request.method == 'POST':
        identifiant = request.POST.get('identifiant', '').strip()
        mot_de_passe = request.POST.get('mot_de_passe', '')

        utilisateur = authenticate(request, username=identifiant, password=mot_de_passe)
        if utilisateur is not None:
            if utilisateur.is_active:
                login(request, utilisateur)
                return redirect('dashboard')
            else:
                message = "Compte désactivé."
        else:
            message = "Identifiant ou mot de passe incorrect."
    return render(request, 'login.html', {'message': message})


# DÉCONNEXION
def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------------------------------------------------------------
# 5) SAUVEGARDE LOCALISATION (AJAX)
# ------------------------------------------------------------------------

@csrf_exempt
def enregistrer_localisation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=400)


# ------------------------------------------------------------------------
# 6) AFFICHER RECOMMANDATIONS SAUVEGARDÉES
# ------------------------------------------------------------------------


@login_required(login_url='login')
def afficher_recommandations(request):
    utilisateur = request.user
    recommandations = Recommandation.objects.filter(utilisateur=utilisateur)
    return render(request, 'mes_recommandations.html', {'recommandations': recommandations})


# ------------------------------------------------------------------------
# 7) FORMULAIRE + PRÉDICTION ML
# ------------------------------------------------------------------------
# AGROYA/agri_re/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import joblib

from .forms import CultureRecommendationForm
from .models import Culture, Recommandation
from .predict import faire_recommandation

# Chemins absolus vers le modèle et les encodeurs générés précédemment
model_path = "C:\\Users\\lenovo\\Downloads\\final pfa\\AGROYA\\ml_models\\xgboost_model_oriente.pkl"
encoders_path = "C:\\Users\\lenovo\\Downloads\\final pfa\\AGROYA\\ml_models\\label_encoders_oriente.pkl"

@login_required(login_url='login')
def recommandation(request):
    form = CultureRecommendationForm(request.POST or None)
    recommandations = None

    if request.method == "POST" and form.is_valid():
        mapped_data = form.get_mapped_data()
        try:
            model = joblib.load(model_path)
            encoders = joblib.load(encoders_path)
        except Exception as e:
            messages.error(request, f"Erreur de chargement du modèle/encodeurs : {e}")
            return render(request, "recommandation.html", {"form": form})

        resultat = faire_recommandation(mapped_data)

        if "erreur" in resultat:
            return render(request, "recommandation.html", {
                "form": form,
                "resultat": {"erreur": resultat["erreur"]}
            })

        recommendations = resultat.get("recommendations", [])
        if not recommendations:
            messages.error(request, "Le modèle n’a retourné aucune recommandation.")
            return render(request, "recommandation.html", {"form": form})

        # (Enregistrement en base facultatif)
        nom_pred = recommendations[0]["nom_culture"]
        culture_obj = Culture.objects.filter(nom_culture__iexact=nom_pred).first()
        if culture_obj:
            Recommandation.objects.create(
                utilisateur=request.user,
                culture=culture_obj,
                recommandations_generales=resultat.get("texte", "")
            )
    
        context = {
            "texte": resultat.get("texte", ""),
            "recommendations": recommendations,
            "texte": resultat.get("texte", "") if 'resultat' in locals() else ""
            
        }
        return render(request, "recommandation_result.html", context)

    # Si GET ou formulaire invalide
    return render(request, "recommandation.html", {"form": form})
    

# ------------------------------------------------------------------------
# 8) LISTES DE CULTURES PAR CATÉGORIE
# ------------------------------------------------------------------------

@login_required(login_url='login')
def legumes(request):
    cultures = Culture.objects.filter(categorie='Légume').order_by('nom_culture')
    return render(request, 'cultures/legumes.html', {'cultures': cultures})


@login_required(login_url='login')
def fruits(request):
    cultures = Culture.objects.filter(categorie='Fruit').order_by('nom_culture')
    return render(request, 'cultures/fruits.html', {'cultures': cultures})


@login_required(login_url='login')
def cereales(request):
    cultures = Culture.objects.filter(categorie='Céréale').order_by('nom_culture')
    return render(request, 'cultures/cereales.html', {'cultures': cultures})




from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Recommandation
@login_required
def export_recommandation_pdf(request, recommandation_id):
    recommandation = get_object_or_404(Recommandation, id=recommandation_id)
    if recommandation.utilisateur != request.user:
        return HttpResponse("Accès refusé.", status=403)

    context = {'recommandation': recommandation}
    html_string = render_to_string('recommandations/recommandation_pdf.html', context)
    pdf = weasyprint.HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recommandation_{recommandation_id}.pdf"'
    return response

@login_required 
def telecharger_pdf_recommandation(request, recommandation_id):
    recommandation = get_object_or_404(Recommandation.objects.select_related('utilisateur', 'culture'), id=recommandation_id)

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    y = 800
    line_height = 20

    utilisateur = recommandation.utilisateur
    nom_utilisateur = utilisateur.nom_complet 

    # Titre
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, "📄 Rapport de Recommandation Agricole"); y -= line_height * 2

    # Données principales
    p.setFont("Helvetica", 12)
    p.drawString(100, y, f"Recommandation ID : {recommandation.id}"); y -= line_height
    p.drawString(100, y, f"Nom de l'utilisateur : {nom_utilisateur}"); y -= line_height
    p.drawString(100, y, f"Email : {utilisateur.email}"); y -= line_height
    p.drawString(100, y, f"Culture recommandée : {recommandation.culture.nom_culture}"); y -= line_height
    p.drawString(100, y, f"Date de création : {recommandation.date_creation.strftime('%d/%m/%Y %H:%M')}"); y -= line_height

    # Conseils
    from textwrap import wrap
    lignes = wrap(recommandation.recommandations_generales, 90)
    y -= line_height
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "📌 Conseils personnalisés :")
    y -= line_height

    p.setFont("Helvetica", 12)
    for ligne in lignes:
        p.drawString(110, y, ligne)
        y -= line_height
        if y < 100:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa

@login_required
def export_recommandation_pdf(request, recommandation_id):
    recommandation = get_object_or_404(
        Recommandation.objects.select_related('utilisateur', 'culture'),
        id=recommandation_id
    )
    template_path = 'agri_re/recommandation_pdf.html'
    context = {'recommandation': recommandation}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recommandation_{recommandation_id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF')
    
    return response


from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from .models import Recommandation

def dashboard_recommandation(request):
    # Récupérer le user connecté
    utilisateur = request.user

    # Récupérer ses recommandations
    recommandations = Recommandation.objects.filter(utilisateur=utilisateur).select_related('culture')

    # Préparer le contexte pour le template
    context = {
        'utilisateur': utilisateur,
        'recommandations': recommandations,
    }

    # Si format=pdf dans l'URL, on génère un PDF
    if request.GET.get('format') == 'pdf':
        # Charger le template HTML en string
        html_string = render_to_string('dashboard/recommandation.html', context)

        # Générer le PDF avec WeasyPrint
        pdf = weasyprint.HTML(string=html_string).write_pdf()

        # Retourner la réponse PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="recommandations.pdf"'
        return response

    # Sinon, afficher la page HTML normalement
    return render(request, 'dashboard/recommandation.html', context)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import WebPushSubscription
import json

@csrf_exempt
@login_required
def save_subscription(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            endpoint = data.get("endpoint")
            keys = data.get("keys", {})
            p256dh = keys.get("p256dh")
            auth = keys.get("auth")

            # Mettre à jour ou créer une nouvelle subscription
            WebPushSubscription.objects.update_or_create(
                user=request.user,
                endpoint=endpoint,
                defaults={"p256dh": p256dh, "auth": auth}
            )

            return JsonResponse({"status": "Abonnement enregistré avec succès"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

from .models import WebPushSubscription
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from webpush import send_user_notification

@login_required
def send_test_notification(request):
    payload = {
        "head": "Recommandation Agricole",
        "body": "Votre recommandation a été générée avec succès ! 🌱",
        "icon": "/static/icons/icon-192x192.png",
        "url": "/dashboard/"
    }
    try:
        send_user_notification(user=request.user, payload=payload, ttl=1000)
        return JsonResponse({"status": "Notification envoyée"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Recommandation

@login_required
def confirmAnnulation(request, recommandation_id):
    recommandation = get_object_or_404(Recommandation, id=recommandation_id, utilisateur=request.user)

    # On suppose qu'on ajoute un champ "statut" et "date_annulation" au modèle Recommandation 
    # pour suivre l'annulation (à ajouter dans ton modèle si pas encore fait)
    recommandations_annulees = Recommandation.objects.filter(
        utilisateur=request.user, statut='annulée'
    ).order_by('-date_annulation')

    nb_annulees = recommandations_annulees.count()

    if request.method == 'POST':
        recommandation.statut = 'annulée'
        recommandation.date_annulation = timezone.now()
        recommandation.save()
        return redirect('dashboard')  # adapter selon ton url

    return render(request, 'confirmAnnulation.html', {
        'recommandation': recommandation,
        'nb_annulees': nb_annulees,
        'recommandations_annulees': recommandations_annulees,
    })

from django.shortcuts import render, redirect
from django.core.cache import cache
from .email_utils import generate_verification_code, send_verification_email
from .models import Utilisateur

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        nom_complet = request.POST.get('nom_complet')

        try:
            user = Utilisateur.objects.get(email=email, nom_complet=nom_complet)
            code = generate_verification_code()

            # Stocker le code temporairement pendant 10 minutes
            cache.set(f'verification_code_{email}', code, timeout=600)

            # Envoyer le mail
            send_verification_email(email, code)

            # Stocker l'email en session
            request.session['reset_email'] = email
            return redirect('verify_code')

        except Utilisateur.DoesNotExist:
            return render(request, 'password_reset_request.html', {'error': "Utilisateur introuvable."})
    
    return render(request, 'password_reset_request.html')

def verify_code(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset_request')

    if request.method == 'POST':
        entered_code = request.POST.get('code')
        stored_code = cache.get(f'verification_code_{email}')

        if stored_code and entered_code == stored_code:
            # Supprimer le code après usage
            cache.delete(f'verification_code_{email}')
            return redirect('set_new_password')
        else:
            return render(request, 'verify_code.html', {'error': "Code incorrect ou expiré."})

    return render(request, 'verify_code.html')

def set_new_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset_request')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            return render(request, 'set_new_password.html', {'error': "Les mots de passe ne correspondent pas."})

        user = Utilisateur.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        request.session.flush()  # Nettoyer la session après réinitialisation
        return redirect('login')

    return render(request, 'set_new_password.html')
from datetime import timedelta
from .models import SuiviCulture, Culture
from .forms import SuiviCultureForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from datetime import timedelta
from .forms import SuiviCultureForm
from .utils import duree_saison_en_jours 
@login_required
def ajouter_suivi(request):
    if request.method == 'POST':
        form = SuiviCultureForm(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.utilisateur = request.user

            # ✅ Calculer la durée selon la saison
            nom_saison = suivi.culture.saisons.strip().capitalize()
            duree = duree_saison_en_jours(nom_saison)
            suivi.date_recolte_prevue = suivi.date_semis + timedelta(days=duree)

            suivi.rappel_arrosage = False  # plus utilisé dans cette logique
            suivi.save()
            # ✅ Envoi de l'email
            send_mail(
                subject="🌱 Suivi de culture enregistré",
                message=(
                    f"Bonjour {request.user.nom_complet},\n\n"
                    f"Votre suivi de la culture '{suivi.culture.nom_culture}' a bien été enregistré.\n"
                    f"Date de semis : {suivi.date_semis.strftime('%d/%m/%Y')}\n"
                    f"Date de récolte prévue : {suivi.date_recolte_prevue.strftime('%d/%m/%Y')}\n\n"
                    "Merci d'utiliser AgroYA !"
                ),
                from_email=None,  # prendra DEFAULT_FROM_EMAIL
                recipient_list=[request.user.email],
                fail_silently=False
            )

            messages.success(request, "✅ Suivi enregistré avec succès. Un email de confirmation vous a été envoyé.")
            return redirect('dashboard')
    else:
        form = SuiviCultureForm()
    return render(request, 'ajouter_suivi.html', {'form': form})

from django.utils import timezone
from .models import SuiviCulture
from webpush import send_user_notification

def envoyer_rappels_automatiques():
    demain = timezone.now().date() + timezone.timedelta(days=1)
    suivis = SuiviCulture.objects.filter(date_prochain_arrosage=demain, rappel_arrosage=True)
    
    for suivi in suivis:
        payload = {
            "head": "Rappel Arrosage 🌱",
            "body": f"Il est temps d'arroser vos {suivi.culture.nom_culture} demain !",
            "icon": "/static/icons/icon-192x192.png",
            "url": "/dashboard/"
        }
        send_user_notification(user=suivi.utilisateur, payload=payload, ttl=1000)
def duree_saison_en_jours(nom_saison):
    durees = {
        'Printemps': 92,
        'Été': 93,
        'Automne': 91,
        'Hiver': 90  # on prend 90 pour simplifier
    }
    return durees.get(nom_saison, 90)  # valeur par défaut si saison inconnue
from django.shortcuts import render
from django.db.models import Count
from .models import Utilisateur
import json

def admin_dashboard(request):
    users_by_region = Utilisateur.objects.values('region').annotate(count=Count('id')).order_by('region')

    regions = [item['region'] for item in users_by_region]
    users_count = [item['count'] for item in users_by_region]


    context = {
        'regions_json': json.dumps(regions),
        'users_count_json': json.dumps(users_count),
    }

    return render(request, 'admin_dashboard.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Utilisateur

@login_required
def update_coords(request):
    if request.method == 'POST':
        try:
            user = request.user
            user.latitude = float(request.POST.get('latitude'))
            user.longitude = float(request.POST.get('longitude'))
            user.save()
            messages.success(request, 'Localisation mise à jour avec succès!')
        except (ValueError, TypeError):
            messages.error(request, 'Veuillez entrer des coordonnées valides')
    
    return redirect('profil')



# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
# from .models import ChatbotMessage # Uncomment if you want to save messages
from .ollama_client import call_ollama_api  # Import the corrected function

@csrf_exempt
@login_required
def ia_chat(request):
    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        if not question:
            return JsonResponse({"error": "Veuillez poser une question."}, status=400)

        # You can adjust this prompt to guide the AI's persona
        prompt = f"""Tu es un assistant expert en agriculture et tu dois répondre aux questions de manière précise et utile.
Question de l'utilisateur : {question}
Réponse de l'assistant :"""

        try:
            # Call the Ollama API using the helper function
            reponse_ia = call_ollama_api(prompt, model="mistral") # Ensure 'mistral' model is downloaded in Ollama

            # Optional: Save the message to the database
            # if request.user.is_authenticated:
            #     ChatbotMessage.objects.create(
            #         utilisateur=request.user,
            #         question=question,
            #         reponse=reponse_ia
            #     )

            return JsonResponse({"response": reponse_ia})

        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error in ia_chat view: {e}")
            return JsonResponse({"error": f"Désolé, je n'ai pas pu générer de réponse pour le moment. Erreur: {str(e)}"}, status=500)

    return JsonResponse({"error": "Méthode non autorisée. Veuillez utiliser POST."}, status=405)

# Keep other views as they are if they are working
from django.shortcuts import render
# from .models import ChatbotMessage # Uncomment if you use ChatbotMessage model

@login_required
def chatbot_history(request):
    # This view assumes you have a ChatbotMessage model and it's properly set up
    # If not, you might need to create it (models.py) and run makemigrations/migrate
    # messages = ChatbotMessage.objects.filter(utilisateur=request.user).order_by('-date')
    messages = [] # Placeholder if ChatbotMessage model is not used
    return render(request, 'chatbot/history.html', {'messages': messages})