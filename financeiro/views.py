from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Conta, Despesa, ItemDespesa
from .forms import DespesaForm
from core.utils import render_to_pdf
from django.utils import timezone
from django.db.models import Sum
from atividades.models import Projeto


class FinanceiroDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'financeiro/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contas'] = Conta.objects.all()
        context['despesas_recentes'] = Despesa.objects.filter(inutilizado=False).order_by('-data_lancamento')[:10]
        context['despesas_inutilizadas'] = Despesa.objects.filter(inutilizado=True).order_by('-data_inutilizacao')[:5]
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
