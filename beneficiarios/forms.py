from django import forms
from django.forms import inlineformset_factory
from .models import Beneficiario, Turno, VinculoBeneficiario
from atividades.models import TipoAtividade, Projeto, Nucleo

class BeneficiarioForm(forms.ModelForm):
    class Meta:
        model = Beneficiario
        fields = [
            'nome_completo', 'data_nascimento', 'cpf', 'telefone', 'foto',
            'tem_problema_saude', 'descricao_saude',
            'necessita_acessibilidade', 'descricao_acessibilidade',
            'responsavel', 'grau_parentesco',
            'observacoes', 'status',
        ]
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }


class VinculoForm(forms.ModelForm):
    class Meta:
        model = VinculoBeneficiario
        fields = ['projeto', 'nucleo', 'atividade', 'turno']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cascata: Projeto → Núcleo
        self.fields['nucleo'].queryset = Nucleo.objects.none()
        # Cascata: Núcleo → Atividade
        self.fields['atividade'].queryset = TipoAtividade.objects.none()
        # Cascata: Atividade → Turno
        self.fields['turno'].queryset = Turno.objects.none()

        if 'projeto' in self.data:
            prefix = self.prefix
            try:
                projeto_id = int(self.data.get(f'{prefix}-projeto'))
                self.fields['nucleo'].queryset = Nucleo.objects.filter(projeto_id=projeto_id).order_by('nome')
                self.fields['atividade'].queryset = TipoAtividade.objects.filter(projeto_id=projeto_id).order_by('nome')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.projeto_id:
            self.fields['nucleo'].queryset = Nucleo.objects.filter(projeto=self.instance.projeto).order_by('nome')
            self.fields['atividade'].queryset = TipoAtividade.objects.filter(projeto=self.instance.projeto).order_by('nome')

        if 'atividade' in self.data:
            prefix = self.prefix
            try:
                atividade_id = int(self.data.get(f'{prefix}-atividade'))
                self.fields['turno'].queryset = Turno.objects.filter(tipoatividade__id=atividade_id).order_by('nome')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.atividade_id:
            self.fields['turno'].queryset = self.instance.atividade.turnos.order_by('nome')


VinculoFormSet = inlineformset_factory(
    Beneficiario,
    VinculoBeneficiario,
    form=VinculoForm,
    fields=['projeto', 'nucleo', 'atividade', 'turno'],
    extra=1,
    can_delete=True,
)
