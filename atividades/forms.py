from django import forms
from django.forms import inlineformset_factory
from .models import Projeto, TipoAtividade, RegistroAtividade

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'ativo']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

# Inline Formset para editar Atividades DENTRO da tela de Projetos
TipoAtividadeFormSet = inlineformset_factory(
    Projeto, 
    TipoAtividade, 
    fields=['nome'], 
    extra=1, 
    can_delete=True
)

class RegistroAtividadeForm(forms.ModelForm):
    class Meta:
        model = RegistroAtividade
        fields = ['projeto', 'tipo_atividade', 'data', 'descricao', 'foto_1', 'foto_2', 'video_1']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
