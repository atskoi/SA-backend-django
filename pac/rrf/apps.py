from django.apps import AppConfig


class RrfConfig(AppConfig):
    name = 'pac.rrf'
    label = 'rrf'

    def ready(self):
        noop = True
#         from pac import scheduler
#         scheduler.start()
