from django.urls import path
from . import views

urlpatterns = [
    path('', views.BeneficiarioListView.as_view(), name='beneficiarios_list'),
    path('novo/', views.BeneficiarioCreateView.as_view(), name='beneficiarios_create'),
    path('editar/<int:pk>/', views.BeneficiarioUpdateView.as_view(), name='beneficiarios_update'),
    path('detalhes/<int:pk>/', views.BeneficiarioDetailView.as_view(), name='beneficiarios_detail'),
    path('relatorios/lista-chamada/', views.ListaChamadaPdfView.as_view(), name='beneficiarios_relatorio_chamada'),
    path('relatorios/por-projeto/', views.RelatorioPorProjetoView.as_view(), name='beneficiarios_relatorio_projeto'),
]
