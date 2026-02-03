from django import forms
from .models import Beneficiario, Turno
from atividades.models import TipoAtividade, Projeto

class BeneficiarioForm(forms.ModelForm):
    class Meta:
        model = Beneficiario
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # HTMX Trigger: Quando mudar o projeto, recarrega o campo 'atividade'
        if 'projeto' in self.fields:
            self.fields['projeto'].widget.attrs.update({
                'hx-get': '/atividades/ajax/load-atividades/',
                'hx-target': '#id_atividade',
                'hx-swap': 'innerHTML'
            })

        # HTMX Trigger: Quando mudar a atividade, recarrega o campo 'turno'
        if 'atividade' in self.fields:
            self.fields['atividade'].widget.attrs.update({
                'hx-get': '/atividades/ajax/load-turnos/',
                'hx-target': '#id_turno',
                'hx-swap': 'innerHTML'
            })

        # Filtragem Inicial (se já tiver projeto selecionado ou se for POST)
        self.fields['atividade'].queryset = TipoAtividade.objects.none()
        self.fields['turno'].queryset = Turno.objects.none()

        if 'projeto' in self.data:
            try:
                projeto_id = int(self.data.get('projeto'))
                self.fields['atividade'].queryset = TipoAtividade.objects.filter(projeto_id=projeto_id).order_by('nome')
            except (ValueError, TypeError):
                pass  # Entrada inválida, mantém queryset vazio
        elif self.instance.pk:
            # Edição: carrega atividades do projeto salvo
            if self.instance.projeto_id:
                self.fields['atividade'].queryset = self.instance.projeto.tipos_atividade.order_by('nome')

        # Lógica para carregar TURNOS baseados na atividade
        if 'atividade' in self.data:
            try:
                atividade_id = int(self.data.get('atividade'))
                self.fields['turno'].queryset = Turno.objects.filter(tipoatividade__id=atividade_id).order_by('nome')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            if self.instance.atividade_id:
                self.fields['turno'].queryset = self.instance.atividade.turnos.order_by('nome')
