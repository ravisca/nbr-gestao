from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Movimentacao

class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'estoque/item_list.html'
    context_object_name = 'itens'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(nome__icontains=busca)
        return queryset.order_by('nome')

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = 'estoque/item_form.html'
    fields = '__all__'
    success_url = reverse_lazy('estoque_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novo Item'
        return context

class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = 'estoque/item_form.html'
    fields = '__all__'
    success_url = reverse_lazy('estoque_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Item'
        return context

class MovimentacaoEntradaView(LoginRequiredMixin, CreateView):
    model = Movimentacao
    template_name = 'estoque/movimentacao_form.html'
    fields = ['item', 'quantidade', 'origem_destino', 'observacao']
    success_url = reverse_lazy('estoque_list')

    def form_valid(self, form):
        form.instance.tipo = 'ENTRADA'
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nova Entrada (Doação/Compra)'
        return context

class MovimentacaoSaidaView(LoginRequiredMixin, CreateView):
    model = Movimentacao
    template_name = 'estoque/movimentacao_form.html'
    fields = ['item', 'quantidade', 'origem_destino', 'observacao']
    success_url = reverse_lazy('estoque_list')

    def form_valid(self, form):
        form.instance.tipo = 'SAIDA'
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nova Saída (Uso/Consumo)'
        return context
