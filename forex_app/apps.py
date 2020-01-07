from django.apps import AppConfig


class ForexAppConfig(AppConfig):
    name = 'forex_app'

    def ready(self):            
        import forex_app.signals