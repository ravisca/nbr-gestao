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
from .models import Item, Movimentacao, Categoria, UnidadeMedida, Emprestimo
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

from django.forms import formset_factory
from django.shortcuts import redirect
from .forms import MovimentacaoSaidaItemForm, SaidaOptionsForm

class MovimentacaoSaidaLoteView(LoginRequiredMixin, View):
    template_name = 'estoque/movimentacao_saida_lote.html'
    
    def get(self, request):
        # Cria um formset com 1 formulário inicial
        MovimentacaoFormSet = formset_factory(MovimentacaoSaidaItemForm, extra=1)
        formset = MovimentacaoFormSet()
        
        # Formulário de Opções (Empréstimo)
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
            
            # Dados do Empréstimo (se houver)
            nome_solicitante = options_form.cleaned_data.get('nome_solicitante')
            contato = options_form.cleaned_data.get('contato')
            data_prevista = options_form.cleaned_data.get('data_prevista')
            
            for form in formset:
                if form.cleaned_data: # Ignora formulários vazios
                    item = form.cleaned_data['item']
                    quantidade = form.cleaned_data['quantidade']
                    
                    if is_emprestimo:
                        # Cria EMPRÉSTIMO
                        Emprestimo.objects.create(
                            item=item,
                            quantidade_emprestada=int(quantidade), # Garante int
                            nome_solicitante=nome_solicitante,
                            contato=contato,
                            data_prevista=data_prevista,
                            interno=True,
                            observacoes="Criado via Saída em Lote"
                        )
                        # A lógica do save() do Emprestimo já baixa o estoque
                        
                    else:
                        # Cria MOVIMENTAÇÃO (Saída Comum)
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
