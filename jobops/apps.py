from django.apps import AppConfig

class JobopsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobops'
    verbose_name = 'JobOps Management System'

    def ready(self):
        import jobops.signals
