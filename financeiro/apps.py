from django.apps import AppConfig


class FinanceiroConfig(AppConfig):
    name = 'financeiro'

    def ready(self):
        import financeiro.signals
