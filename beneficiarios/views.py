from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Beneficiario
from core.utils import render_to_pdf
from django.utils import timezone

class BeneficiarioListView(LoginRequiredMixin, ListView):
    model = Beneficiario
    template_name = 'beneficiarios/beneficiario_list.html'
    context_object_name = 'beneficiarios'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(nome_completo__icontains=busca)
        return queryset.order_by('nome_completo')

class BeneficiarioCreateView(LoginRequiredMixin, CreateView):
    model = Beneficiario
    template_name = 'beneficiarios/beneficiario_form.html'
    fields = '__all__'
    success_url = reverse_lazy('beneficiarios_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novo Beneficiário'
        return context

class BeneficiarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Beneficiario
    template_name = 'beneficiarios/beneficiario_form.html'
    fields = '__all__'
    success_url = reverse_lazy('beneficiarios_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Beneficiário'
        return context

class BeneficiarioDetailView(LoginRequiredMixin, DetailView):
    model = Beneficiario
    template_name = 'beneficiarios/beneficiario_detail.html'
    context_object_name = 'beneficiario'

class ListaChamadaPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Filtra apenas ativos para a lista de chamada
        beneficiarios = Beneficiario.objects.filter(status='ATIVO').order_by('nome_completo')
        
        context = {
            'beneficiarios': beneficiarios,
            'data_geracao': timezone.now(),
            'usuario': request.user,
        }
        
        return render_to_pdf('beneficiarios/relatorio_chamada.html', context)
