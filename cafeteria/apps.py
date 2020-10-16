from django.apps import AppConfig


class CafeteriaConfig(AppConfig):
    name = 'cafeteria'

    def ready(self):
        import cafeteria.signals
