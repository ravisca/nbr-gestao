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

        projeto_id = None
        atividade_id = None
        
        # 1. Tenta recuperar valores iniciais da instância (quando editando um registro existente)
        if self.instance.pk:
            if self.instance.projeto_id:
                projeto_id = self.instance.projeto_id
            if self.instance.atividade_id:
                atividade_id = self.instance.atividade_id

        # 2. Sobrescreve pelos valores do POST (self.data) se existirem. 
        # Como é formset, a chave exata depende do prefix (ex: vinculos-0-projeto)
        if self.data:
            prefix = self.prefix if self.prefix else ''
            # Tenta pegar a chave com e sem prefixo, ou procura por chaves terminadas no campo correto
            p_key = f'{prefix}-projeto'
            a_key = f'{prefix}-atividade'
            
            if p_key in self.data and self.data[p_key]:
                try:
                    projeto_id = int(self.data[p_key])
                except (ValueError, TypeError):
                    pass
                    
            if a_key in self.data and self.data[a_key]:
                try:
                    atividade_id = int(self.data[a_key])
                except (ValueError, TypeError):
                    pass

        # 3. Aplica os filtros permitindo apenas opções daquele projeto/atividade
        if projeto_id:
            self.fields['nucleo'].queryset = Nucleo.objects.filter(projeto_id=projeto_id).order_by('nome')
            self.fields['atividade'].queryset = TipoAtividade.objects.filter(projeto_id=projeto_id).order_by('nome')
            
        if atividade_id:
            self.fields['turno'].queryset = Turno.objects.filter(tipoatividade__id=atividade_id).order_by('nome')


VinculoFormSet = inlineformset_factory(
    Beneficiario,
    VinculoBeneficiario,
    form=VinculoForm,
    fields=['projeto', 'nucleo', 'atividade', 'turno'],
    extra=1,
    can_delete=True,
)
