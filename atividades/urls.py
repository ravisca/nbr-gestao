from django.urls import path
from .views import registrar_atividade_view, sucesso_view

urlpatterns = [
    path('registrar/', registrar_atividade_view, name='registrar_atividade_mobile'),
    path('sucesso/', sucesso_view, name='sucesso_mobile'),
]