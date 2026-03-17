from django.urls import path
from . import views

urlpatterns = [
    path('itens/', views.ItemListView.as_view(), name='estoque_list'),
    path('item/novo/', views.ItemCreateView.as_view(), name='estoque_item_create'),
    path('item/editar/<int:pk>/', views.ItemUpdateView.as_view(), name='estoque_item_update'),

    path('movimentacao/entrada/', views.MovimentacaoEntradaView.as_view(), name='estoque_entrada'),
    path('movimentacao/saida/', views.MovimentacaoSaidaView.as_view(), name='estoque_saida'),

    # Empréstimos
    path('emprestimos/', views.EmprestimoListView.as_view(), name='estoque_emprestimo_list'),
    path('emprestimos/externo/novo/', views.EmprestimoExternoCreateView.as_view(), name='estoque_emprestimo_externo'),
    path('emprestimos/interno/novo/', views.EmprestimoInternoCreateView.as_view(), name='estoque_emprestimo_interno'),
    path('emprestimos/devolucao/<int:pk>/', views.EmprestimoDevolucaoView.as_view(), name='estoque_emprestimo_devolucao'),

    # Relatórios e Recibos
    path('relatorio/', views.RelatorioEstoquePdfView.as_view(), name='estoque_relatorio_movimentacao'),
    path('relatorio/emprestimos/', views.RelatorioEmprestimoView.as_view(), name='estoque_relatorio_emprestimos'),
    path('recibo/movimentacao/<str:grupo_lote>/', views.ReciboMovimentacaoPdfView.as_view(), name='estoque_recibo_movimentacao'),
    path('recibo/emprestimo/<str:grupo_lote>/', views.ReciboEmprestimoPdfView.as_view(), name='estoque_recibo_emprestimo'),

    # AJAX / Quick Add
    path('ajax/categoria/nova/', views.CategoriaCreatePopup.as_view(), name='estoque_categoria_create_ajax'),
    path('ajax/unidade/nova/', views.UnidadeCreatePopup.as_view(), name='estoque_unidade_create_ajax'),
]
