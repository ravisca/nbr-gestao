from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import RegistroAtividade, Projeto, TipoAtividade, Nucleo
from financeiro.models import ItemDespesa
from .forms import ProjetoForm, TipoAtividadeFormSet, NucleoFormSet, RegistroAtividadeForm, NaturezaDespesaFormSet

# --- Permissões ---
def eh_monitor_ou_admin(user):
    return user.has_perm('atividades.add_registroatividade') or user.is_staff

def eh_admin(user):
    return user.is_staff

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(name='Núcleo').exists()

class ViewProjectRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(name__in=['Núcleo', 'Operacional']).exists()

# --- Views de Gestão de Projetos (CRUD Master-Detail) ---
class ProjetoListView(LoginRequiredMixin, ViewProjectRequiredMixin, ListView):
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
            data['nucleos'] = NucleoFormSet(self.request.POST)
            data['atividades'] = TipoAtividadeFormSet(self.request.POST)
            data['naturezas'] = NaturezaDespesaFormSet(self.request.POST)
        else:
            data['nucleos'] = NucleoFormSet()
            data['atividades'] = TipoAtividadeFormSet()
            data['naturezas'] = NaturezaDespesaFormSet()
        data['titulo'] = 'Novo Projeto'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        nucleos = context['nucleos']
        atividades = context['atividades']
        naturezas = context['naturezas']
        with transaction.atomic():
            self.object = form.save()
            if nucleos.is_valid() and atividades.is_valid() and naturezas.is_valid():
                nucleos.instance = self.object
                nucleos.save()
                atividades.instance = self.object
                atividades.save()
                naturezas.instance = self.object
                naturezas.save()
            else:
                return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)

class ProjetoDetailView(LoginRequiredMixin, ViewProjectRequiredMixin, DetailView):
    model = Projeto
    template_name = 'atividades/projeto_detail.html'
    context_object_name = 'projeto'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['titulo'] = f'Visualizar Projeto: {self.object.nome}'
        return data

class ProjetoUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Projeto
    form_class = ProjetoForm
    template_name = 'atividades/projeto_form.html'
    success_url = reverse_lazy('projeto_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['nucleos'] = NucleoFormSet(self.request.POST, instance=self.object)
            data['atividades'] = TipoAtividadeFormSet(self.request.POST, instance=self.object)
            data['naturezas'] = NaturezaDespesaFormSet(self.request.POST, instance=self.object)
        else:
            data['nucleos'] = NucleoFormSet(instance=self.object)
            data['atividades'] = TipoAtividadeFormSet(instance=self.object)
            data['naturezas'] = NaturezaDespesaFormSet(instance=self.object)
        data['titulo'] = 'Editar Projeto'
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        nucleos = context['nucleos']
        atividades = context['atividades']
        naturezas = context['naturezas']
        with transaction.atomic():
            self.object = form.save()
            if nucleos.is_valid() and atividades.is_valid() and naturezas.is_valid():
                nucleos.save()
                atividades.save()
                naturezas.save()

                # Coleta alertas de itens duplicados ignorados
                itens_ignorados_total = []
                for nat_form in naturezas.forms:
                    if hasattr(nat_form, 'nomes_ignorados_warning_buffer'):
                        itens_ignorados_total.extend(nat_form.nomes_ignorados_warning_buffer)

                if itens_ignorados_total:
                    from django.contrib import messages
                    itens_str = ", ".join(itens_ignorados_total)
                    if len(itens_ignorados_total) == 1:
                        msg = f"O item rápido '{itens_str}' não foi criado pois já existia um item com este nome."
                    else:
                        msg = f"Os seguintes {len(itens_ignorados_total)} itens rápidos não foram criados pois já existiam com o mesmo nome: {itens_str}."
                    messages.warning(self.request, msg)

            else:
                return self.render_to_response(self.get_context_data(form=form))
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
@login_required
def load_atividades(request):
    projeto_id = request.GET.get('projeto')
    nucleo_id = request.GET.get('nucleo')
    if nucleo_id:
        atividades = TipoAtividade.objects.filter(nucleo_id=nucleo_id).order_by('nome')
    elif projeto_id:
        atividades = TipoAtividade.objects.filter(projeto_id=projeto_id).order_by('nome')
    else:
        atividades = TipoAtividade.objects.none()
    return render(request, 'atividades/atividade_dropdown_list_options.html', {'atividades': atividades})

@login_required
def load_turnos(request):
    atividade_id = request.GET.get('atividade')
    print(f"[DEBUG] load_turnos invoked. atividade_id={atividade_id}")
    from beneficiarios.models import Turno  # Local import to avoid circular dependencies if any

    if atividade_id:
        try:
            atividade = TipoAtividade.objects.get(pk=atividade_id)
            turnos = atividade.turnos.all().order_by('nome')
            print(f"[DEBUG] Found {turnos.count()} turnos for Atividade {atividade.nome}")
        except TipoAtividade.DoesNotExist:
             print("[DEBUG] TipoAtividade.DoesNotExist")
             turnos = Turno.objects.none()
    else:
        print("[DEBUG] No atividade_id provided")
        turnos = Turno.objects.none()
    return render(request, 'atividades/turno_dropdown_list_options.html', {'turnos': turnos})

@login_required
def load_nucleos(request):
    projeto_id = request.GET.get('projeto')
    if projeto_id:
        nucleos = Nucleo.objects.filter(projeto_id=projeto_id).order_by('nome')
    else:
        nucleos = Nucleo.objects.none()
    return render(request, 'atividades/nucleo_dropdown_list_options.html', {'nucleos': nucleos})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
@require_POST
def delete_item_despesa(request, item_id):
    print(f"BATEU NA VIEW delete_item_despesa COM ID {item_id}")
    try:
        item = ItemDespesa.objects.get(id=item_id)
        if not eh_admin(request.user):
            print(f"USUARIO {request.user} NAO EH ADMIN!")
            return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
        item.delete()
        print("ITEM EXCLUIDO COM SUCESSO!")
        return JsonResponse({'success': True})
    except ItemDespesa.DoesNotExist:
        print(f"ITEM {item_id} NAO EXISTE NA BASE!")
        return JsonResponse({'success': False, 'error': 'Item não encontrado'}, status=404)


# --- Painel de Atividades Registradas ---
from django.contrib.auth.models import User as AuthUser
from core.utils import render_to_pdf
from django.utils import timezone as tz

class AtividadePainelView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = RegistroAtividade
    template_name = 'atividades/atividade_painel.html'
    context_object_name = 'atividades'
    ordering = ['-data', '-id']

    def get_paginate_by(self, queryset):
        return self.request.GET.get('per_page', 10)

    def get_queryset(self):
        queryset = super().get_queryset().select_related('projeto', 'tipo_atividade', 'monitor')

        projeto = self.request.GET.get('projeto')
        if projeto:
            queryset = queryset.filter(projeto_id=projeto)

        monitor = self.request.GET.get('monitor')
        if monitor:
            queryset = queryset.filter(monitor_id=monitor)

        data_inicio = self.request.GET.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)

        data_fim = self.request.GET.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)

        busca = self.request.GET.get('busca')
        if busca:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(descricao__icontains=busca) |
                Q(tipo_atividade__nome__icontains=busca) |
                Q(observacoes__icontains=busca)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projetos'] = Projeto.objects.filter(ativo=True).order_by('nome')
        context['monitores'] = AuthUser.objects.filter(
            registroatividade__isnull=False
        ).distinct().order_by('first_name', 'last_name')
        context['projeto_selecionado'] = self.request.GET.get('projeto', '')
        context['monitor_selecionado'] = self.request.GET.get('monitor', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['busca'] = self.request.GET.get('busca', '')
        return context


class RelatorioAtividadePdfView(LoginRequiredMixin, AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        queryset = RegistroAtividade.objects.select_related(
            'projeto', 'tipo_atividade', 'monitor'
        ).order_by('-data', '-id')

        projeto_id = request.GET.get('projeto')
        if projeto_id:
            queryset = queryset.filter(projeto_id=projeto_id)

        monitor_id = request.GET.get('monitor')
        if monitor_id:
            queryset = queryset.filter(monitor_id=monitor_id)

        data_inicio = request.GET.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)

        data_fim = request.GET.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)

        # Construir descrição dos filtros aplicados
        filtros = []
        if projeto_id:
            p = Projeto.objects.filter(pk=projeto_id).first()
            if p:
                filtros.append(f"Projeto: {p.nome}")
        if monitor_id:
            m = AuthUser.objects.filter(pk=monitor_id).first()
            if m:
                filtros.append(f"Monitor: {m.get_full_name() or m.username}")
        if data_inicio:
            filtros.append(f"De: {data_inicio}")
        if data_fim:
            filtros.append(f"Até: {data_fim}")

        context = {
            'atividades': queryset,
            'filtros': ' | '.join(filtros) if filtros else 'Todos os registros',
            'total': queryset.count(),
            'data_geracao': tz.now(),
            'usuario': request.user,
        }
        return render_to_pdf('atividades/relatorio_atividades.html', context)
