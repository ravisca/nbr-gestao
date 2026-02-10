from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Movimentacao, Emprestimo
from django.views import View
from core.utils import render_to_pdf
from django.utils import timezone


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

from .forms import ItemForm

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'estoque/item_form.html'
    success_url = reverse_lazy('estoque_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novo Item'
        return context

class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'estoque/item_form.html'
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

class RelatorioEstoquePdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        hoje = timezone.now()
        mes = request.GET.get('mes', hoje.strftime('%m'))
        ano = request.GET.get('ano', hoje.year)

        # 1. Entradas e Saídas (Model Movimentacao)
        movimentacoes = Movimentacao.objects.filter(data__month=mes, data__year=ano).order_by('data')
        entradas = movimentacoes.filter(tipo='ENTRADA')
        saidas = movimentacoes.filter(tipo='SAIDA')

        # 2. Empréstimos (Model Emprestimo)
        # Empréstimos feitos no mês (data_saida)
        emprestimos_saida = Emprestimo.objects.filter(data_saida__month=mes, data_saida__year=ano).order_by('data_saida')
        
        # Empréstimos devolvidos no mês (data_devolucao)
        emprestimos_retorno = Emprestimo.objects.filter(data_devolucao__month=mes, data_devolucao__year=ano, devolvido=True).order_by('data_devolucao')

        context = {
            'entradas': entradas,
            'saidas': saidas,
            'emprestimos_saida': emprestimos_saida,
            'emprestimos_retorno': emprestimos_retorno,
            'mes': mes,
            'ano': ano,
            'data_geracao': hoje,
            'usuario': request.user,
        }

        return render_to_pdf('estoque/relatorio_movimentacao.html', context)


# --- QUICK ADD VIEWS ---
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .models import Categoria, UnidadeMedida
from django.forms import modelform_factory

class GenericPopupCreateView(View):
    model = None
    fields = '__all__'
    title = "Adicionar"

    def get(self, request, *args, **kwargs):
        FormClass = modelform_factory(self.model, fields=self.fields)
        form = FormClass()
        return HttpResponse(render_to_string('estoque/quick_add_form.html', {'form': form, 'titulo': self.title, 'action_url': request.path}, request=request))

    def post(self, request, *args, **kwargs):
        FormClass = modelform_factory(self.model, fields=self.fields)
        form = FormClass(request.POST)
        if form.is_valid():
            obj = form.save()
            return JsonResponse({'success': True, 'id': obj.id, 'name': str(obj)})
        else:
            return JsonResponse({'success': False, 'form_html': render_to_string('estoque/quick_add_form.html', {'form': form, 'titulo': self.title, 'action_url': request.path}, request=request)})

class CategoriaCreatePopup(GenericPopupCreateView):
    model = Categoria
    fields = ['nome']
    title = "Nova Categoria"

class UnidadeCreatePopup(GenericPopupCreateView):
    model = UnidadeMedida
    fields = ['nome', 'sigla']
    title = "Nova Unidade de Medida"
