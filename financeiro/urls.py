from django.urls import path
from . import views

urlpatterns = [
    path('', views.FinanceiroDashboardView.as_view(), name='financeiro_dashboard'),
    path('receita/nova/', views.ReceitaCreateView.as_view(), name='financeiro_receita_create'),
    path('despesa/nova/', views.DespesaCreateView.as_view(), name='financeiro_despesa_create'),
    path('relatorios/prestacao-contas/', views.RelatorioFinanceiroPdfView.as_view(), name='financeiro_relatorio_prestacao'),
]
