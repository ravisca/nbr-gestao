from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from .models import Beneficiario, VinculoBeneficiario
from .forms import BeneficiarioForm, VinculoFormSet
from core.utils import render_to_pdf
from django.utils import timezone
from atividades.models import Projeto

class BeneficiarioListView(LoginRequiredMixin, ListView):
    model = Beneficiario
    template_name = 'beneficiarios/beneficiario_list.html'
    context_object_name = 'beneficiarios'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('vinculos__projeto', 'vinculos__turno')
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(nome_completo__icontains=busca)
        return queryset.order_by('nome_completo')

class BeneficiarioCreateView(LoginRequiredMixin, CreateView):
    model = Beneficiario
    form_class = BeneficiarioForm
    template_name = 'beneficiarios/beneficiario_form.html'
    success_url = reverse_lazy('beneficiarios_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novo Beneficiário'
        if self.request.POST:
            context['vinculos'] = VinculoFormSet(self.request.POST)
        else:
            context['vinculos'] = VinculoFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        vinculos = context['vinculos']
        with transaction.atomic():
            self.object = form.save()
            if vinculos.is_valid():
                vinculos.instance = self.object
                vinculos.save()
            else:
                return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)

class BeneficiarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Beneficiario
    form_class = BeneficiarioForm
    template_name = 'beneficiarios/beneficiario_form.html'
    success_url = reverse_lazy('beneficiarios_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Beneficiário'
        if self.request.POST:
            context['vinculos'] = VinculoFormSet(self.request.POST, instance=self.object)
        else:
            context['vinculos'] = VinculoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        vinculos = context['vinculos']
        with transaction.atomic():
            self.object = form.save()
            if vinculos.is_valid():
                vinculos.save()
            else:
                return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)

class BeneficiarioDetailView(LoginRequiredMixin, DetailView):
    model = Beneficiario
    template_name = 'beneficiarios/beneficiario_detail.html'
    context_object_name = 'beneficiario'

class ListaChamadaPdfView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        beneficiarios = Beneficiario.objects.filter(status='ATIVO').order_by('nome_completo')
        
        context = {
            'beneficiarios': beneficiarios,
            'data_geracao': timezone.now(),
            'usuario': request.user,
        }
        
        return render_to_pdf('beneficiarios/relatorio_chamada.html', context)

class RelatorioPorProjetoView(LoginRequiredMixin, ListView):
    template_name = 'beneficiarios/relatorio_projeto.html'
    context_object_name = 'beneficiarios'

    def get_queryset(self):
        projeto_id = self.request.GET.get('projeto')
        if projeto_id:
            return Beneficiario.objects.filter(
                vinculos__projeto_id=projeto_id
            ).distinct().prefetch_related('vinculos__projeto', 'vinculos__atividade', 'vinculos__turno').order_by('nome_completo')
        return Beneficiario.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projetos'] = Projeto.objects.filter(ativo=True).order_by('nome')
        context['projeto_selecionado'] = self.request.GET.get('projeto', '')
        return context
