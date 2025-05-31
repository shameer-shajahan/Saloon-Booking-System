from django.apps import AppConfig


class SalonAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'salon_app'
    
    def ready(self):
        # Import signals
        import salon_app.signals
