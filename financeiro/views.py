from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Conta, Receita, Despesa, ItemDespesa
from .forms import DespesaForm
from core.utils import render_to_pdf
from django.utils import timezone
from django.db.models import Sum

class FinanceiroDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'financeiro/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contas'] = Conta.objects.all()
        context['receitas_recentes'] = Receita.objects.order_by('-data', '-id')[:5]
        context['despesas_recentes'] = Despesa.objects.order_by('-data_lancamento')[:5]
        return context

class ReceitaCreateView(LoginRequiredMixin, CreateView):
    model = Receita
    template_name = 'financeiro/lancamento_form.html'
    fields = ['conta', 'categoria', 'valor', 'data', 'descricao']
    success_url = reverse_lazy('financeiro_dashboard')

    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nova Receita (Entrada)'
        context['cor'] = 'success'
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

class RelatorioFinanceiroPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Default para o mês atual se não informado
        hoje = timezone.now()
        mes = request.GET.get('mes', hoje.strftime('%m'))
        ano = request.GET.get('ano', hoje.year)
        
        # Filtros
        despesas = Despesa.objects.filter(mes_referencia=mes, ano_referencia=ano).order_by('data_emissao')
        receitas = Receita.objects.filter(data__month=mes, data__year=ano).order_by('data')
        
        # Totais
        total_despesas = despesas.aggregate(Sum('valor'))['valor__sum'] or 0
        total_receitas = receitas.aggregate(Sum('valor'))['valor__sum'] or 0
        saldo_periodo = total_receitas - total_despesas
        
        context = {
            'despesas': despesas,
            'receitas': receitas,
            'total_despesas': total_despesas,
            'total_receitas': total_receitas,
            'saldo_periodo': saldo_periodo,
            'mes': mes,
            'ano': ano,
            'data_geracao': hoje,
            'usuario': request.user,
        }
        
        return render_to_pdf('financeiro/relatorio_prestacao.html', context)

def load_itens_despesa(request):
    projeto_id = request.GET.get('projeto')
    itens = []
    if projeto_id:
        # Traz itens ordenados por natureza
        itens = ItemDespesa.objects.filter(natureza__projeto_id=projeto_id).order_by('natureza__codigo', 'codigo')
    return render(request, 'financeiro/item_dropdown_list_options.html', {'itens': itens})
