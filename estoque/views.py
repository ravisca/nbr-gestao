import copy
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
from .forms import ItemForm, DevolucaoForm
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


# === LOTE VIEW BASE ===
import uuid
from django.forms import formset_factory

class GenericLoteCreateView(LoginRequiredMixin, View):
    header_form_class = None
    item_form_class = None
    template_name = 'estoque/movimentacao_lote_form.html'
    titulo = "Movimentação em Lote"
    success_url = reverse_lazy('estoque_list')

    def processar_lote(self, header_form, formset, grupo_lote):
        raise NotImplementedError("Subclasses devem implementar processar_lote")

    def get(self, request):
        ItemFormSet = formset_factory(self.item_form_class, extra=1)
        header_form = self.header_form_class()
        formset = ItemFormSet(prefix='itens')
        return render(request, self.template_name, {
            'header_form': header_form,
            'formset': formset,
            'titulo': self.titulo
        })

    def post(self, request):
        ItemFormSet = formset_factory(self.item_form_class)
        header_form = self.header_form_class(request.POST)
        formset = ItemFormSet(request.POST, prefix='itens')

        if header_form.is_valid() and formset.is_valid():
            grupo_lote = str(uuid.uuid4().hex)[:10].upper()
            with transaction.atomic():
                self.processar_lote(header_form, formset, grupo_lote)
            
            tipo = 'EMPRESTIMO' if 'Empréstimo' in self.titulo else 'MOVIMENTACAO'
            
            return render(request, 'estoque/lote_sucesso.html', {
                'grupo_lote': grupo_lote,
                'tipo': tipo,
                'url_voltar': self.success_url
            })

        return render(request, self.template_name, {
            'header_form': header_form,
            'formset': formset,
            'titulo': self.titulo
        })


# === MOVIMENTAÇÕES ===

from .forms import MovimentacaoHeaderForm, MovimentacaoEntradaItemForm, MovimentacaoSaidaItemForm

class MovimentacaoEntradaView(GenericLoteCreateView):
    header_form_class = MovimentacaoHeaderForm
    item_form_class = MovimentacaoEntradaItemForm
    titulo = 'Nova Entrada Lote (Doação/Compra)'

    def processar_lote(self, header_form, formset, grupo_lote):
        origem = header_form.cleaned_data.get('origem_destino')
        observacao = header_form.cleaned_data.get('observacao')
        
        for f in formset:
            if f.cleaned_data:
                Movimentacao.objects.create(
                    item=f.cleaned_data['item'],
                    tipo='ENTRADA',
                    quantidade=f.cleaned_data['quantidade'],
                    usuario=self.request.user,
                    origem_destino=origem,
                    observacao=observacao,
                    grupo_lote=grupo_lote
                )

class MovimentacaoSaidaView(GenericLoteCreateView):
    header_form_class = MovimentacaoHeaderForm
    item_form_class = MovimentacaoSaidaItemForm
    titulo = 'Nova Saída Lote (Uso/Consumo)'

    def processar_lote(self, header_form, formset, grupo_lote):
        destino = header_form.cleaned_data.get('origem_destino')
        observacao = header_form.cleaned_data.get('observacao')
        
        for f in formset:
            if f.cleaned_data:
                Movimentacao.objects.create(
                    item=f.cleaned_data['item'],
                    tipo='SAIDA',
                    quantidade=f.cleaned_data['quantidade'],
                    usuario=self.request.user,
                    origem_destino=destino,
                    observacao=observacao,
                    grupo_lote=grupo_lote
                )


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

from .forms import EmprestimoExternoHeaderForm, EmprestimoInternoHeaderForm, EmprestimoItemForm, EmprestimoEditForm

class EmprestimoExternoCreateView(GenericLoteCreateView):
    header_form_class = EmprestimoExternoHeaderForm
    item_form_class = EmprestimoItemForm
    titulo = 'Novo Empréstimo Externo (Lote)'
    success_url = reverse_lazy('estoque_emprestimo_list')

    def processar_lote(self, header_form, formset, grupo_lote):
        base_emp = header_form.save(commit=False)
        for f in formset:
            if f.cleaned_data:
                emp = copy.copy(base_emp)
                emp.pk = None
                emp.id = None
                emp.tipo = 'EXTERNO'
                emp.grupo_lote = grupo_lote
                emp.item = f.cleaned_data['item']
                emp.quantidade_emprestada = f.cleaned_data['quantidade']
                emp.save()

class EmprestimoInternoCreateView(GenericLoteCreateView):
    header_form_class = EmprestimoInternoHeaderForm
    item_form_class = EmprestimoItemForm
    titulo = 'Novo Empréstimo Interno / Operação (Lote)'
    success_url = reverse_lazy('estoque_emprestimo_list')

    def processar_lote(self, header_form, formset, grupo_lote):
        base_emp = header_form.save(commit=False)
        for f in formset:
            if f.cleaned_data:
                emp = copy.copy(base_emp)
                emp.pk = None
                emp.id = None
                emp.tipo = 'INTERNO'
                emp.grupo_lote = grupo_lote
                emp.item = f.cleaned_data['item']
                emp.quantidade_emprestada = f.cleaned_data['quantidade']
                emp.save()

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


class EmprestimoUpdateView(LoginRequiredMixin, UpdateView):
    model = Emprestimo
    form_class = EmprestimoEditForm
    template_name = 'estoque/emprestimo_form.html'
    success_url = reverse_lazy('estoque_emprestimo_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Empréstimo #{self.object.pk}'
        context['tipo_emprestimo'] = self.object.tipo
        context['is_edit'] = True
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


class ReciboMovimentacaoPdfView(LoginRequiredMixin, View):
    def get(self, request, grupo_lote):
        movimentacoes = Movimentacao.objects.filter(grupo_lote=grupo_lote)
        if not movimentacoes.exists():
            return HttpResponse("Recibo não encontrado ou lote inválido.")
        
        primeira = movimentacoes.first()
        context = {
            'is_emprestimo': False,
            'itens': movimentacoes,
            'data': primeira.data,
            'origem_destino': primeira.origem_destino,
            'observacao': primeira.observacao,
            'tipo': primeira.get_tipo_display(),
            'grupo_lote': grupo_lote,
            'data_geracao': timezone.now(),
            'usuario': primeira.usuario,
            'titulo': f"Comprovante de {primeira.get_tipo_display()}"
        }
        return render_to_pdf('estoque/recibo_pdf.html', context)

class ReciboEmprestimoPdfView(LoginRequiredMixin, View):
    def get(self, request, grupo_lote):
        emprestimos = Emprestimo.objects.filter(grupo_lote=grupo_lote)

        # Fallback: if grupo_lote is actually a pk (for loans without batch)
        if not emprestimos.exists():
            try:
                emp_by_pk = Emprestimo.objects.filter(pk=int(grupo_lote))
                if emp_by_pk.exists():
                    emprestimos = emp_by_pk
            except (ValueError, TypeError):
                pass

        if not emprestimos.exists():
            return HttpResponse("Recibo de empréstimo não encontrado ou lote inválido.")

        primeiro = emprestimos.first()
        context = {
            'is_emprestimo': True,
            'itens': emprestimos,
            'data': primeiro.data_saida,
            'data_real': primeiro.data_saida_real,
            'solicitante': primeiro.nome_solicitante,
            'cpf': primeiro.cpf_solicitante,
            'email': primeiro.email_solicitante,
            'endereco': primeiro.endereco,
            'responsavel_casa': primeiro.responsavel_casa,
            'logistica': primeiro.logistica,
            'contato': primeiro.contato,
            'previsao': primeiro.data_prevista,
            'projeto': primeiro.projeto,
            'nucleo': primeiro.nucleo,
            'observacao': primeiro.observacoes,
            'tipo': primeiro.get_tipo_display(),
            'tipo_emprestimo': primeiro.tipo,
            'grupo_lote': grupo_lote,
            'data_geracao': timezone.now(),
            'usuario': request.user,
            'titulo': f"Comprovante de Empréstimo ({primeiro.get_tipo_display()})"
        }
        return render_to_pdf('estoque/recibo_pdf.html', context)
