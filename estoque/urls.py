from django.urls import path
from . import views

urlpatterns = [
    path('itens/', views.ItemListView.as_view(), name='estoque_list'),
    path('item/novo/', views.ItemCreateView.as_view(), name='estoque_item_create'),
    path('item/editar/<int:pk>/', views.ItemUpdateView.as_view(), name='estoque_item_update'),
    
    path('movimentacao/entrada/', views.MovimentacaoEntradaView.as_view(), name='estoque_entrada'),
    path('movimentacao/saida/', views.MovimentacaoSaidaView.as_view(), name='estoque_saida'),
    
    path('relatorio/', views.RelatorioEstoquePdfView.as_view(), name='estoque_relatorio_movimentacao'),
    
    # AJAX / Quick Add
    path('ajax/categoria/nova/', views.CategoriaCreatePopup.as_view(), name='estoque_categoria_create_ajax'),
    path('ajax/unidade/nova/', views.UnidadeCreatePopup.as_view(), name='estoque_unidade_create_ajax'),
]
