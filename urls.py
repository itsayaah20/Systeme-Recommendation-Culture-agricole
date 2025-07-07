# AGROYA/agri_re/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views 
from agri_re.views import export_recommandation_pdf
from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static







urlpatterns = [
    path('', views.home_view, name='home'),
    path('accueil/', views.page_accueil, name='accueil'),
    path('profil/', views.profil_utilisateur, name='profil'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('update-coords/', views.update_coords, name='update_coords'),
    path('services/', views.services, name='services'),
    path('base/',  views.base_page, name='base'),
    path('signup/', views.signup, name='signup'),
    path('recommandation/', views.recommandation, name='recommandation'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/recommandation/', views.recommandation, name='recommandation'),
    path('recherche/', views.recherche, name='recherche'),
    path('enregistrer-localisation/', views.enregistrer_localisation, name='enregistrer_localisation'),
    path('recommandations/', views.afficher_recommandations, name='recommandations'),
    path('login/signup/', views.signup, name='signup_alt'),
    path('login/signup/login/', views.login_view, name='login_nested'),
    path('login/signup/login/signup/', views.signup, name='signup_nested'),
    path('dashboard/cultures/Légume/', views.legumes, name='legumes'),
    path('dashboard/cultures/Fruit/', views.fruits, name='fruits'),
    path('dashboard/cultures/Céréale/', views.cereales, name='cereales'),
    path('dashboard/recommandation/', views.dashboard_recommandation, name='dashboard_recommandation'),
    path('recommandation/<int:recommandation_id>/telecharger/', views.telecharger_pdf_recommandation, name='telecharger_pdf_recommandation'),
    path('service-worker.js', TemplateView.as_view(template_name="service-worker.js", content_type='application/javascript'), name='service-worker'),
    path('webpush/save-subscription/', views.save_subscription, name='save_subscription'),
    path('webpush/send-test/', views.send_test_notification, name='send_test_notification'),
    path('export_pdf/', views.export_recommandation_pdf, name='export_pdf'),
    path('recommandation/<int:recommandation_id>/export/', views.export_recommandation_pdf, name='export_recommandation_pdf'),
    path('recommandation/<int:recommandation_id>/confirm_annulation/', views.confirmAnnulation, name='confirm_annulation'),
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('verify_code/', views.verify_code, name='verify_code'),
    path('set_new_password/', views.set_new_password, name='set_new_password'),
    path('ajouter-suivi/', views.ajouter_suivi, name='ajouter_suivi'),
    path('chatbot/history/', views.chatbot_history, name='chatbot_history'),
    path('ia-chat/', views.ia_chat, name='ia_chat'),






]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
