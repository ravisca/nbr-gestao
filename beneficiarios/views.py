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
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        projeto = self.request.GET.get('projeto')
        if projeto:
            queryset = queryset.filter(vinculos__projeto_id=projeto).distinct()
            
        busca = self.request.GET.get('busca')
        if busca:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(nome_completo__icontains=busca) |
                Q(cpf__icontains=busca) |
                Q(telefone__icontains=busca)
            )
            
        return queryset.order_by('nome_completo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        status_selecionado = self.request.GET.get('status', '')
        context['status_ativo_flag'] = 'selected' if status_selecionado == 'ATIVO' else ''
        context['status_inativo_flag'] = 'selected' if status_selecionado == 'INATIVO' else ''
        
        projeto_id_str = self.request.GET.get('projeto', '')
        try:
            projeto_selecionado_int = int(projeto_id_str)
        except ValueError:
            projeto_selecionado_int = None
            
        projetos = list(Projeto.objects.filter(ativo=True).order_by('nome'))
        for p in projetos:
            p.selected_flag = 'selected' if p.pk == projeto_selecionado_int else ''
            
        context['projetos'] = projetos
        return context

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
        beneficiarios = Beneficiario.objects.all()
        
        status = request.GET.get('status')
        if status:
            beneficiarios = beneficiarios.filter(status=status)
        else:
            beneficiarios = beneficiarios.filter(status='ATIVO')
            
        projeto = request.GET.get('projeto')
        if projeto:
            beneficiarios = beneficiarios.filter(vinculos__projeto_id=projeto).distinct()
            
        busca = request.GET.get('busca')
        if busca:
            from django.db.models import Q
            beneficiarios = beneficiarios.filter(
                Q(nome_completo__icontains=busca) |
                Q(cpf__icontains=busca) |
                Q(telefone__icontains=busca)
            )
            
        beneficiarios = beneficiarios.order_by('nome_completo')
        
        context = {
            'beneficiarios': beneficiarios,
            'data_geracao': timezone.now(),
            'usuario': request.user,
        }
        
        return render_to_pdf('beneficiarios/relatorio_chamada.html', context)

class RelatorioPorProjetoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        projeto_id = request.GET.get('projeto')
        if not projeto_id:
            return render(request, 'core/error.html', {'message': 'Projeto não informado.'})
            
        projeto = Projeto.objects.filter(pk=projeto_id).first()
        if not projeto:
             return render(request, 'core/error.html', {'message': 'Projeto não encontrado.'})

        from django.db.models import Prefetch
        
        vinculos_prefetch = Prefetch(
            'vinculos',
            queryset=VinculoBeneficiario.objects.filter(projeto_id=projeto_id).select_related('projeto', 'atividade', 'turno')
        )

        beneficiarios = Beneficiario.objects.filter(
            vinculos__projeto_id=projeto_id,
            status='ATIVO'
        ).distinct().prefetch_related(vinculos_prefetch).order_by('nome_completo')
        
        context = {
            'beneficiarios': beneficiarios,
            'projeto_titulo': projeto.nome,
            'data_geracao': timezone.now(),
            'usuario': request.user,
        }
        
        return render_to_pdf('beneficiarios/relatorio_chamada.html', context)
