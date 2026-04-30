from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Conta, Despesa, ItemDespesa, LogExclusaoFinanceiro
from .forms import DespesaForm
from core.utils import render_to_pdf
from django.utils import timezone
from django.db.models import Sum
from atividades.models import Projeto
from django.core.paginator import Paginator


class FinanceiroDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'financeiro/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtros
        conta_id = self.request.GET.get('conta')
        busca = self.request.GET.get('busca')
        
        despesas_base = Despesa.objects.all()
        if conta_id:
            despesas_base = despesas_base.filter(conta_id=conta_id)
        if busca:
            from django.db.models import Q
            despesas_base = despesas_base.filter(
                Q(razao_social__icontains=busca) |
                Q(nota_fiscal__icontains=busca)
            )

        context['projetos'] = Projeto.objects.filter(ativo=True).order_by('nome')
        context['conta_selecionada'] = int(conta_id) if conta_id and conta_id.isdigit() else None
        context['busca'] = busca or ''
        context['contas'] = Conta.objects.all()
        
        # Paginação das despesas principais (ex "recentes")
        despesas_ativas = despesas_base.filter(inutilizado=False).order_by('-data_lancamento')
        per_page = self.request.GET.get('per_page', 10)
        paginator = Paginator(despesas_ativas, per_page)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context['despesas_recentes'] = page_obj
        context['page_obj'] = page_obj
        context['paginator'] = paginator
        context['is_paginated'] = page_obj.has_other_pages()
        
        context['despesas_inutilizadas'] = despesas_base.filter(inutilizado=True).order_by('-data_inutilizacao')[:10]
        return context


class DespesaCreateView(LoginRequiredMixin, CreateView):
    model = Despesa
    form_class = DespesaForm
    template_name = 'financeiro/lancamento_form.html'
    success_url = reverse_lazy('financeiro_dashboard')

    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nova Despesa (Saída)'
        context['cor'] = 'danger'
        return context


class DespesaInutilizarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        despesa = get_object_or_404(Despesa, pk=pk)
        motivo = request.POST.get('motivo', '')
        despesa.inutilizar(motivo=motivo)
        messages.success(request, f'Despesa #{despesa.pk} inutilizada com sucesso. Saldo devolvido à conta.')
        return redirect('financeiro_dashboard')

class DespesaDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        despesa = get_object_or_404(Despesa, pk=pk)
        justificativa = request.POST.get('justificativa', '')
        
        if not justificativa:
            messages.error(request, 'Justificativa é obrigatória para exclusão.')
            return redirect('financeiro_dashboard')

        # Devolver saldo se não estava inutilizada
        if not despesa.inutilizado and despesa.conta:
            despesa.conta.saldo_atual += despesa.valor
            despesa.conta.save()

        # Registrar log
        LogExclusaoFinanceiro.objects.create(
            despesa_id=despesa.pk,
            valor=despesa.valor,
            razao_social=despesa.razao_social,
            usuario=request.user,
            justificativa=justificativa
        )
        
        despesa_pk = despesa.pk
        despesa.delete()
        messages.success(request, f'Despesa #{despesa_pk} excluída permanentemente. Log registrado e saldo estornado.')
        return redirect('financeiro_dashboard')


class RelatorioFinanceiroPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        hoje = timezone.now()
        mes = request.GET.get('mes', hoje.strftime('%m'))
        ano = request.GET.get('ano', hoje.year)
        projeto_id = request.GET.get('projeto')

        # Base queryset: apenas despesas ativas, ordem cronológica
        despesas = Despesa.objects.filter(
            inutilizado=False,
            mes_referencia=mes,
            ano_referencia=ano
        ).order_by('data_emissao')

        # Filtro por projeto
        if projeto_id:
            despesas = despesas.filter(projeto_id=projeto_id)

        # Total (linha de soma)
        total_despesas = despesas.aggregate(Sum('valor'))['valor__sum'] or 0

        # Projetos para o filtro
        projetos = Projeto.objects.all().order_by('nome')

        context = {
            'despesas': despesas,
            'total_despesas': total_despesas,
            'mes': mes,
            'ano': ano,
            'data_geracao': hoje,
            'usuario': request.user,
            'projetos': projetos,
            'projeto_selecionado': int(projeto_id) if projeto_id else None,
        }

        return render_to_pdf('financeiro/relatorio_prestacao.html', context)


def load_itens_despesa(request):
    projeto_id = request.GET.get('projeto')
    itens = []
    if projeto_id:
        itens = ItemDespesa.objects.filter(natureza__projeto_id=projeto_id).order_by('natureza__codigo', 'codigo')
    return render(request, 'financeiro/item_dropdown_list_options.html', {'itens': itens})
