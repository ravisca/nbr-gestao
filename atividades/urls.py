from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_atividade_view, name='registrar_atividade_mobile'),
    path('sucesso/', views.sucesso_view, name='sucesso_mobile'),
    
    # Gestão de Projetos
    path('projetos/', views.ProjetoListView.as_view(), name='projeto_list'),
    path('projetos/novo/', views.ProjetoCreateView.as_view(), name='projeto_create'),
    path('projetos/editar/<int:pk>/', views.ProjetoUpdateView.as_view(), name='projeto_update'),

    # AJAX
    path('ajax/load-atividades/', views.load_atividades, name='ajax_load_atividades'),
]