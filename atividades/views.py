from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction

from .models import RegistroAtividade, Projeto, TipoAtividade
from .forms import ProjetoForm, TipoAtividadeFormSet, RegistroAtividadeForm

# --- Permissões ---
def eh_monitor_ou_admin(user):
    return user.has_perm('atividades.add_registroatividade') or user.is_staff

def eh_admin(user):
    return user.is_staff

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# --- Views de Gestão de Projetos (CRUD Master-Detail) ---
class ProjetoListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Projeto
    template_name = 'atividades/projeto_list.html'
    context_object_name = 'projetos'

class ProjetoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = 'atividades/projeto_form.html'
    success_url = reverse_lazy('projeto_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['atividades'] = TipoAtividadeFormSet(self.request.POST)
        else:
            data['atividades'] = TipoAtividadeFormSet()
        data['titulo'] = 'Novo Projeto'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        atividades = context['atividades']
        with transaction.atomic():
            self.object = form.save()
            if atividades.is_valid():
                atividades.instance = self.object
                atividades.save()
        return super().form_valid(form)

class ProjetoUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = 'atividades/projeto_form.html'
    success_url = reverse_lazy('projeto_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['atividades'] = TipoAtividadeFormSet(self.request.POST, instance=self.object)
        else:
            data['atividades'] = TipoAtividadeFormSet(instance=self.object)
        data['titulo'] = 'Editar Projeto'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        atividades = context['atividades']
        with transaction.atomic():
            self.object = form.save()
            if atividades.is_valid():
                atividades.save()
        return super().form_valid(form)

# --- Views Operacionais (Mobile) ---

@login_required
@user_passes_test(eh_monitor_ou_admin)
def registrar_atividade_view(request):
    if request.method == 'POST':
        form = RegistroAtividadeForm(request.POST, request.FILES)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.monitor = request.user 
            atividade.save()
            messages.success(request, 'Atividade registrada com sucesso!')
            return redirect('sucesso_mobile')
    else:
        from django.utils import timezone
        form = RegistroAtividadeForm(initial={'data': timezone.now().date()})

    return render(request, 'atividades/mobile_form.html', {'form': form})

@login_required
def sucesso_view(request):
    return render(request, 'atividades/sucesso.html')

# --- AJAX HTMX ---
def load_atividades(request):
    projeto_id = request.GET.get('projeto')
    if projeto_id:
        atividades = TipoAtividade.objects.filter(projeto_id=projeto_id).order_by('nome')
    else:
        atividades = TipoAtividade.objects.none()
    return render(request, 'atividades/atividade_dropdown_list_options.html', {'atividades': atividades})

# --- AJAX HTMX ---
def load_atividades(request):
    projeto_id = request.GET.get('projeto')
    if projeto_id:
        atividades = TipoAtividade.objects.filter(projeto_id=projeto_id).order_by('nome')
    else:
        atividades = TipoAtividade.objects.none()
    return render(request, 'atividades/atividade_dropdown_list_options.html', {'atividades': atividades})