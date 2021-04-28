from django.apps import AppConfig


class RenderConfig(AppConfig):
    name = 'render'

    def ready(self):
        import render.signals
        return super().ready()
