"""from django.apps import AppConfig
class MaintenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maintenance'
    """
# maintenance/apps.py

from django.apps import AppConfig

class MaintenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maintenance'

    def ready(self):
        # Évite l'exécution pendant les migrations, tests, ou shell
        import sys
        if any(cmd in sys.argv for cmd in ['migrate', 'test', 'shell', 'makemigrations', 'init_donnees']):
            return
        
        # Charge les données seulement si l'app est 'maintenance' et que la BDD est vide
        try:
            from .models import TypeFiche
            if TypeFiche.objects.count() == 0:
                from .initial_data import load_initial_data
                load_initial_data()
                print("✅ [AUTO] Données initiales chargées avec succès !")
        except Exception:
            # La table n'existe pas encore (première migration)
            pass