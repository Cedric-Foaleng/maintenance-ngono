from django.apps import AppConfig

class MaintenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maintenance'

    def ready(self):
        # Chargement des données initiales au démarrage
        try:
            from .initial_data import load_initial_data
            load_initial_data()
        except Exception:
            # On évite de bloquer le démarrage si la base n'est pas prête (migrations)
            pass
