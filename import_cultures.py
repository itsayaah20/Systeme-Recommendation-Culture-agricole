from django.core.management.base import BaseCommand
from agri_re.models import Culture

class Command(BaseCommand):
    help = 'Import des cultures dans la base de données'

    def handle(self, *args, **options):
        cultures_data = [
            {
                'nom_culture': 'Blé',
                'type_sol': 'Argileux',
                'ph_min': 6.0,
                'ph_max': 7.5,
                'temperature_optimale': 20.0,
                'pluviometrie_min': 300,
                'pluviometrie_max': 600,
                'irrigation': 'oui',
                'budget_min': 8000,
                'budget_max': 15000,
                'saisons': 'Automne,Printemps',
                'benefices': 'Rotation idéale,Peu de maladies,Bon rendement'
            },
            {
                'nom_culture': 'Tomate',
                'type_sol': 'Sableux',
                'ph_min': 6.0,
                'ph_max': 7.0,
                'temperature_optimale': 22.0,
                'pluviometrie_min': 400,
                'pluviometrie_max': 800,
                'irrigation': 'oui',
                'budget_min': 12000,
                'budget_max': 25000,
                'saisons': 'Printemps,Été',
                'benefices': 'Haute valeur marchande,Rotation courte,Bon rendement'
            },
            {
                'nom_culture': 'Orge',
                'type_sol': 'Sableux',
                'ph_min': 6.5,
                'ph_max': 7.5,
                'temperature_optimale': 16.0,
                'pluviometrie_min': 250,
                'pluviometrie_max': 500,
                'irrigation': 'non',
                'budget_min': 7000,
                'budget_max': 13000,
                'saisons': 'Automne,Printemps',
                'benefices': 'Rotation idéale,Peu d\'eau,Bon rendement'
            },
            {
                'nom_culture': 'Poivron',
                'type_sol': 'Argileux',
                'ph_min': 6.0,
                'ph_max': 7.0,
                'temperature_optimale': 22.0,
                'pluviometrie_min': 400,
                'pluviometrie_max': 800,
                'irrigation': 'oui',
                'budget_min': 12000,
                'budget_max': 25000,
                'saisons': 'Printemps,Été',
                'benefices': 'Haute valeur marchande,Rotation courte,Bon rendement'
            },
            {
                'nom_culture': 'Concombre',
                'type_sol': 'Sableux',
                'ph_min': 6.0,
                'ph_max': 7.5,
                'temperature_optimale': 20.0,
                'pluviometrie_min': 300,
                'pluviometrie_max': 600,
                'irrigation': 'oui',
                'budget_min': 10000,
                'budget_max': 20000,
                'saisons': 'Printemps,Été',
                'benefices': 'Rotation idéale,Haute valeur marchande,Bon rendement'
            }
        ]

        for data in cultures_data:
            culture, created = Culture.objects.update_or_create(
                nom_culture=data['nom_culture'],
                defaults={
                    'type_sol': data['type_sol'],
                    'ph_min': data['ph_min'],
                    'ph_max': data['ph_max'],
                    'temperature_optimale': data['temperature_optimale'],
                    'pluviometrie_min': data['pluviometrie_min'],
                    'pluviometrie_max': data['pluviometrie_max'],
                    'irrigation': data['irrigation'],
                    'budget_min': data['budget_min'],
                    'budget_max': data['budget_max'],
                    'saisons': data['saisons'],
                    'benefices': data['benefices']
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Culture '{culture.nom_culture}' {'créée' if created else 'mise à jour'}"))
