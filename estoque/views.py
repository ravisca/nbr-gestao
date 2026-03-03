from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.forms import modelform_factory, formset_factory
from django.utils import timezone
from django.db import transaction

from .models import Item, Movimentacao, Emprestimo, Categoria, UnidadeMedida
from .forms import ItemForm, EmprestimoExternoForm, EmprestimoInternoForm, DevolucaoForm, MovimentacaoSaidaItemForm, SaidaOptionsForm
from core.utils import render_to_pdf


# === ITENS ===

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


# === MOVIMENTAÇÕES ===

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


# === EMPRÉSTIMOS ===

class EmprestimoListView(LoginRequiredMixin, ListView):
    model = Emprestimo
    template_name = 'estoque/emprestimo_list.html'
    context_object_name = 'emprestimos'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        tipo = self.request.GET.get('tipo')
        if status == 'pendente':
            queryset = queryset.filter(devolvido=False)
        elif status == 'devolvido':
            queryset = queryset.filter(devolvido=True)
        if tipo in ('EXTERNO', 'INTERNO'):
            queryset = queryset.filter(tipo=tipo)
        return queryset

class EmprestimoExternoCreateView(LoginRequiredMixin, CreateView):
    model = Emprestimo
    form_class = EmprestimoExternoForm
    template_name = 'estoque/emprestimo_form.html'
    success_url = reverse_lazy('estoque_emprestimo_list')

    def form_valid(self, form):
        form.instance.tipo = 'EXTERNO'
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novo Empréstimo Externo'
        context['tipo_emprestimo'] = 'EXTERNO'
        return context

class EmprestimoInternoCreateView(LoginRequiredMixin, CreateView):
    model = Emprestimo
    form_class = EmprestimoInternoForm
    template_name = 'estoque/emprestimo_form.html'
    success_url = reverse_lazy('estoque_emprestimo_list')

    def form_valid(self, form):
        form.instance.tipo = 'INTERNO'
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novo Empréstimo Interno / Operação'
        context['tipo_emprestimo'] = 'INTERNO'
        return context

class EmprestimoDevolucaoView(LoginRequiredMixin, UpdateView):
    model = Emprestimo
    form_class = DevolucaoForm
    template_name = 'estoque/emprestimo_devolucao.html'
    success_url = reverse_lazy('estoque_emprestimo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar Devolução'
        context['emprestimo'] = self.object
        return context


# === RELATÓRIOS ===

class RelatorioEstoquePdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        hoje = timezone.now()
        mes = request.GET.get('mes', hoje.strftime('%m'))
        ano = request.GET.get('ano', hoje.year)

        movimentacoes = Movimentacao.objects.filter(data__month=mes, data__year=ano).order_by('data')
        entradas = movimentacoes.filter(tipo='ENTRADA')
        saidas = movimentacoes.filter(tipo='SAIDA')
        emprestimos_saida = Emprestimo.objects.filter(data_saida__month=mes, data_saida__year=ano).order_by('data_saida')
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


class RelatorioEmprestimoView(LoginRequiredMixin, ListView):
    model = Emprestimo
    template_name = 'estoque/relatorio_emprestimos.html'
    context_object_name = 'emprestimos'

    def get_queryset(self):
        queryset = super().get_queryset()
        tipo = self.request.GET.get('tipo')
        if tipo in ('EXTERNO', 'INTERNO'):
            queryset = queryset.filter(tipo=tipo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_selecionado'] = self.request.GET.get('tipo', '')
        return context


# === QUICK ADD & BATCH ===

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


class MovimentacaoSaidaLoteView(LoginRequiredMixin, View):
    template_name = 'estoque/movimentacao_saida_lote.html'

    def get(self, request):
        MovimentacaoFormSet = formset_factory(MovimentacaoSaidaItemForm, extra=1)
        formset = MovimentacaoFormSet()
        options_form = SaidaOptionsForm()
        return render(request, self.template_name, {
            'formset': formset,
            'options_form': options_form,
            'titulo': 'Saída em Lote / Empréstimo Interno'
        })

    def post(self, request):
        MovimentacaoFormSet = formset_factory(MovimentacaoSaidaItemForm)
        formset = MovimentacaoFormSet(request.POST)
        options_form = SaidaOptionsForm(request.POST)

        if formset.is_valid() and options_form.is_valid():
            is_emprestimo = options_form.cleaned_data.get('is_emprestimo')
            nome_solicitante = options_form.cleaned_data.get('nome_solicitante')
            contato = options_form.cleaned_data.get('contato')
            data_prevista = options_form.cleaned_data.get('data_prevista')

            for form in formset:
                if form.cleaned_data:
                    item = form.cleaned_data['item']
                    quantidade = form.cleaned_data['quantidade']

                    if is_emprestimo:
                        Emprestimo.objects.create(
                            item=item,
                            quantidade_emprestada=int(quantidade),
                            nome_solicitante=nome_solicitante,
                            contato=contato,
                            data_prevista=data_prevista,
                            tipo='INTERNO',
                            observacoes="Criado via Saída em Lote"
                        )
                    else:
                        Movimentacao.objects.create(
                            item=item,
                            tipo='SAIDA',
                            quantidade=quantidade,
                            usuario=request.user,
                            observacao="Saída em Lote"
                        )
            return redirect('estoque_list')

        return render(request, self.template_name, {
            'formset': formset,
            'options_form': options_form,
            'titulo': 'Saída em Lote / Empréstimo Interno'
        })
