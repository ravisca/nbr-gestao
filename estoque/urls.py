from django.urls import path
from . import views

urlpatterns = [
    path('itens/', views.ItemListView.as_view(), name='estoque_list'),
    path('item/novo/', views.ItemCreateView.as_view(), name='estoque_item_create'),
    path('item/editar/<int:pk>/', views.ItemUpdateView.as_view(), name='estoque_item_update'),
    
    path('movimentacao/entrada/', views.MovimentacaoEntradaView.as_view(), name='estoque_entrada'),
    path('movimentacao/saida/', views.MovimentacaoSaidaView.as_view(), name='estoque_saida'),
]
