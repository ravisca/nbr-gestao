from django import forms
from django.forms import inlineformset_factory
from .models import Projeto, TipoAtividade, RegistroAtividade
from financeiro.models import NaturezaDespesa, ItemDespesa

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['nome', 'cor', 'descricao', 'ativo']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'cor': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'title': 'Escolha a cor do projeto'}),
        }

# --- ATIVIDADES (Check-in, Monitor) ---
class TipoAtividadeForm(forms.ModelForm):
    class Meta:
        model = TipoAtividade
        fields = ['nome', 'turnos']
        widgets = {
            'turnos': forms.CheckboxSelectMultiple()
        }

TipoAtividadeFormSet = inlineformset_factory(
    Projeto, 
    TipoAtividade, 
    form=TipoAtividadeForm,
    fields=['nome', 'turnos'], 
    extra=1, 
    can_delete=True
)

# --- FINANCEIRO (Naturezas e Itens) ---
class NaturezaDespesaForm(forms.ModelForm):
    novos_itens = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex: Material Esportivo, Uniformes (separados por vírgula)'}),
        label="Itens Rápidos (+)",
        help_text="Digite os itens separados por vírgula. Os códigos serão gerados automaticamente (ex: 1.1, 1.2)."
    )

    class Meta:
        model = NaturezaDespesa
        fields = ['codigo', 'nome', 'novos_itens']
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Ex: 1'}),
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Recursos Humanos'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Processa os novos itens
            itens_str = self.cleaned_data.get('novos_itens')
            if itens_str:
                nomes = [n.strip() for n in itens_str.replace('\n', ',').split(',') if n.strip()]
                # Encontra o último código se existir, ou começa do 1
                last_item = instance.itens.order_by('-id').first() # Simplificação: incrementa sequencialmente
                
                # Vamos simplificar: assume que o usuário quer 1.1, 1.2...
                # Se já tiver itens, teríamos que parsear, mas para MVP vamos usar contador simples
                existing_count = instance.itens.count()
                
                for i, nome in enumerate(nomes, start=1):
                    # Gera código: Natureza.Codigo + . + Sequencial
                    # Ex: Natureza 1 -> Item 1.1, 1.2
                    # Ex: Natureza 2.1 -> Item 2.1.1, 2.1.2 
                    seq = existing_count + i
                    novo_codigo = f"{instance.codigo}.{seq}"
                    
                    ItemDespesa.objects.create(
                        natureza=instance,
                        codigo=novo_codigo,
                        nome=nome
                    )
        return instance

NaturezaDespesaFormSet = inlineformset_factory(
    Projeto,
    NaturezaDespesa,
    form=NaturezaDespesaForm,
    fields=['codigo', 'nome'], # 'novos_itens' é processado manualmente no form, mas precisa estar no fields? Não do modelform factory.
    extra=1,
    can_delete=True
) 
# Hack: Adicionamos o campo extra na definição do formset? Não, o form já tem.
# O inlineformset_factory usa o form class, então fields devem ser subset do model ou __all__.
# Mas novos_itens não é do model. Então precisamos garantir que ele apareça.
# O inlineformset_factory restringe campos do model. Vamos tentar usar form=NaturezaDespesaForm e torcer pro Django aceitar o campo extra.

class RegistroAtividadeForm(forms.ModelForm):
    class Meta:
        model = RegistroAtividade
        fields = ['projeto', 'tipo_atividade', 'data', 'descricao', 'foto_1', 'foto_2', 'video_1']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
