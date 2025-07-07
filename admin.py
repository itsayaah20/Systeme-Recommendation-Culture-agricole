from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import (
    Utilisateur,
    Recommandation,
    Culture,
    Meteo,
)
from django.utils.html import format_html


@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    model = Utilisateur
    list_display = ('email', 'cne', 'nom_complet', 'genre', 'region', 'telephone', 'type_agriculture', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'cne', 'nom_complet')
    list_filter = ('region', 'type_agriculture', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('cne', 'nom_complet', 'genre', 'telephone', 'region', 'type_agriculture', 'adresse', 'latitude', 'longitude')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'cne', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )


@admin.register(Recommandation)
class RecommandationAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'culture', 'date_creation']
    list_filter = ['date_creation']


@admin.register(Culture)
class CultureAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />'.format(obj.image.url))
        return None
    image_tag.short_description = 'Image'

    list_display = (
        'nom_culture',
        'categorie',
        'image_tag',
        'type_sol',
        'ph_min',
        'ph_max',
        'temperature_optimale',
        'pluviometrie_min',
        'pluviometrie_max',
        'irrigation',
        'budget_min',
        'budget_max',
    )
    list_filter = ('categorie', 'type_sol', 'irrigation')
    ordering = ('nom_culture',)

@admin.register(Meteo)
class MeteoAdmin(admin.ModelAdmin):
    list_display = ('region', 'date_rapport', 'temperature_min', 'temperature_max', 'humidite_min', 'humidite_max', 'precipitation')
    list_filter = ('region', 'date_rapport')
    search_fields = ('region',)

from .models import ChatbotMessage

@admin.register(ChatbotMessage)
class ChatbotMessageAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'question', 'reponse', 'date')
    search_fields = ('question', 'reponse', 'utilisateur__email')
