from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import RegistroAtividade
from django.forms import modelform_factory

# Função para verificar se é Monitor ou Staff
def eh_monitor_ou_admin(user):
    # Verifica permissão específica em vez de nome de grupo hardcoded
    return user.has_perm('atividades.add_registroatividade') or user.is_staff

# Criamos um formulário automático baseado no Modelo
AtividadeForm = modelform_factory(RegistroAtividade, 
    fields=['projeto', 'tipo_atividade', 'data', 'descricao', 'foto_1', 'foto_2', 'video_1'],
    # Removemos campos que o sistema preenche sozinho (Monitor, Data Registro)
)

@login_required
@user_passes_test(eh_monitor_ou_admin)
def registrar_atividade_view(request):
    if request.method == 'POST':
        # Atenção ao request.FILES para fotos/vídeos funcionarem!
        form = AtividadeForm(request.POST, request.FILES)
        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.monitor = request.user # Preenche o monitor automaticamente
            atividade.save()
            messages.success(request, 'Atividade registrada com sucesso!')
            return redirect('sucesso_mobile')
    else:
        # Preenche a data de hoje automaticamente no formulário vazio
        from django.utils import timezone
        form = AtividadeForm(initial={'data': timezone.now().date()})

    return render(request, 'atividades/mobile_form.html', {'form': form})

@login_required
def sucesso_view(request):
    return render(request, 'atividades/sucesso.html')