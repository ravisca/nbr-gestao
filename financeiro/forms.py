from django import forms
from .models import Despesa, ItemDespesa

class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = ['projeto', 'item', 'razao_social', 'cnpj', 'nota_fiscal', 'serie', 'data_emissao', 'valor', 'mes_referencia', 'ano_referencia', 'observacoes', 'comprovante']
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtro Dinâmico: Se tiver projeto selecionado (POST ou instância), filtra os itens
        if 'projeto' in self.data:
            try:
                projeto_id = int(self.data.get('projeto'))
                self.fields['item'].queryset = ItemDespesa.objects.filter(natureza__projeto_id=projeto_id).order_by('natureza__codigo', 'codigo')
            except (ValueError, TypeError):
                pass  # Valor inválido, mantém queryset vazio ou padrão
        elif self.instance.pk and self.instance.projeto:
            self.fields['item'].queryset = ItemDespesa.objects.filter(natureza__projeto=self.instance.projeto).order_by('natureza__codigo', 'codigo')
        else:
            # Se não tem projeto selecionado, mostra nada ou todos? Melhor mostrar nada para forçar seleção
            self.fields['item'].queryset = ItemDespesa.objects.none()
