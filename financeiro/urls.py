from django.urls import path
from . import views

urlpatterns = [
    path('', views.FinanceiroDashboardView.as_view(), name='financeiro_dashboard'),
    path('despesa/nova/', views.DespesaCreateView.as_view(), name='financeiro_despesa_create'),
    path('despesa/<int:pk>/inutilizar/', views.DespesaInutilizarView.as_view(), name='financeiro_despesa_inutilizar'),
    path('relatorios/prestacao-contas/', views.RelatorioFinanceiroPdfView.as_view(), name='financeiro_relatorio_prestacao'),
    path('ajax/load-itens/', views.load_itens_despesa, name='ajax_load_itens'),
]
