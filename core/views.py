
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from .forms import UsuarioCreationForm, UsuarioUpdateForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

class UsuarioListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'core/usuario_list.html'
    context_object_name = 'usuarios'
    ordering = ['username']

class UsuarioCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = User
    form_class = UsuarioCreationForm
    template_name = 'core/usuario_form.html'
    success_url = reverse_lazy('usuario_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Novo Usuário'
        return context

class UsuarioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioUpdateForm
    template_name = 'core/usuario_form.html'
    success_url = reverse_lazy('usuario_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Usuário'
        return context
