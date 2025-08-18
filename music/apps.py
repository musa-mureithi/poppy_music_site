from django.apps import AppConfig

class MusicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'music'

    def ready(self):
        import music.signals  # This ensures the signal is connected when Django starts
