from django.apps import AppConfig


class DjangoNativeCallConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'native_call'

    def ready(self):
        pass
