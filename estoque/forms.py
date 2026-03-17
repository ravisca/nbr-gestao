from django import forms
from .models import Item, Emprestimo, Movimentacao
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML, Div

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        
        self.helper.layout = Layout(
            Row(
                Column('nome', css_class='col-md-12 mb-3'),
            ),
            Row(
                Column(
                    Div(
                        Field('categoria', wrapper_class=''),
                        HTML('<a href="#" class="btn btn-outline-secondary quick-add-btn" data-url="/estoque/ajax/categoria/nova/" data-target="#id_categoria" title="Nova Categoria"><i class="bi bi-plus-lg"></i></a>'),
                        css_class="input-group"
                    ),
                    css_class='col-md-6 mb-3'
                ),
                Column(
                    Div(
                        Field('unidade', wrapper_class=''),
                        HTML('<a href="#" class="btn btn-outline-secondary quick-add-btn" data-url="/estoque/ajax/unidade/nova/" data-target="#id_unidade" title="Nova Unidade"><i class="bi bi-plus-lg"></i></a>'),
                        css_class="input-group"
                    ),
                    css_class='col-md-6 mb-3'
                ),
            ),
            Row(
                Column('quantidade_atual', css_class='col-md-6 mb-3'),
                Column('estoque_minimo', css_class='col-md-6 mb-3'),
            ),
        )


class EmprestimoExternoHeaderForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = [
            'nome_solicitante', 'cpf_solicitante', 'contato', 'email_solicitante', 'endereco',
            'responsavel_casa', 'data_saida', 'data_saida_real', 'data_prevista', 'observacoes',
        ]
        widgets = {
            'data_saida': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_saida_real': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_prevista': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
        
        # Optional fields
        opcionais = ['observacoes', 'cpf_solicitante', 'email_solicitante', 'endereco', 'data_saida_real', 'responsavel_casa']
        for op in opcionais:
            if op in self.fields:
                self.fields[op].required = False


class EmprestimoInternoHeaderForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = [
            'projeto', 'nucleo', 'nome_solicitante', 'contato',
            'responsavel_casa', 'data_saida', 'data_saida_real', 'data_prevista',
            'logistica', 'observacoes',
        ]
        widgets = {
            'data_saida': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_saida_real': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_prevista': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'logistica': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
            
        opcionais = ['observacoes', 'logistica', 'data_saida_real', 'projeto', 'nucleo', 'responsavel_casa']
        for op in opcionais:
            if op in self.fields:
                self.fields[op].required = False


class EmprestimoItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all().order_by('nome'), label="Item", widget=forms.Select(attrs={'class': 'form-select select2-item'}))
    quantidade = forms.IntegerField(label="Qtd. Levada", widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '1'}))

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantidade = cleaned_data.get('quantidade')
        if item and quantidade:
            if item.quantidade_atual < quantidade:
                self.add_error('quantidade', f"Estoque insuficiente. Saldo disponível: {item.quantidade_atual}")
        return cleaned_data


class DevolucaoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = ['quantidade_devolvida', 'data_devolucao', 'motivo_falta']
        widgets = {
            'data_devolucao': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'motivo_falta': forms.Textarea(attrs={'rows': 3}),
        }


class MovimentacaoHeaderForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['origem_destino', 'observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 2}),
        }


class MovimentacaoEntradaItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all().order_by('nome'), label="Item", widget=forms.Select(attrs={'class': 'form-select select2-item'}))
    quantidade = forms.IntegerField(label="Quantidade", widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '1'}))
    # Sem clean() de validação de estoque negativo, porque é entrada.


class MovimentacaoSaidaItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all().order_by('nome'), label="Item", widget=forms.Select(attrs={'class': 'form-select select2-item'}))
    quantidade = forms.IntegerField(label="Quantidade", widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '1'}))

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantidade = cleaned_data.get('quantidade')
        if item and quantidade:
            if item.quantidade_atual < quantidade:
                self.add_error('quantidade', f"Estoque insuficiente para {item.nome}. Disponível: {item.quantidade_atual}")
        return cleaned_data
