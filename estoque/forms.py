from django import forms
from .models import Item
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML, Div

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False # We handle the form tag in the template
        
        # Define the layout with input groups for Categoria and Unidade
        self.helper.layout = Layout(
            Row(
                Column('nome', css_class='col-md-12 mb-3'),
            ),
            Row(
                # Categoria with + Button
                Column(
                    Div(
                        Field('categoria', wrapper_class=''),
                        HTML('<a href="#" class="btn btn-outline-secondary quick-add-btn" data-url="/estoque/ajax/categoria/nova/" data-target="#id_categoria" title="Nova Categoria"><i class="bi bi-plus-lg"></i></a>'),
                        css_class="input-group"
                    ),
                    css_class='col-md-6 mb-3'
                ),
                # Unidade with + Button
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

class MovimentacaoSaidaItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all().order_by('nome'), label="Item", widget=forms.Select(attrs={'class': 'form-select select2'}))
    quantidade = forms.IntegerField(label="Quantidade", widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}))

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantidade = cleaned_data.get('quantidade')

        if item and quantidade:
            if item.quantidade_atual < quantidade:
                self.add_error('quantidade', f"Estoque insuficiente para {item.nome}. Disponível: {item.quantidade_atual}")
        return cleaned_data

class SaidaOptionsForm(forms.Form):
    # Opção para marcar se é empréstimo interno
    is_emprestimo = forms.BooleanField(required=False, label="É Empréstimo Interno?", widget=forms.CheckboxInput(attrs={'onchange': 'toggleLoanFields()'}))
    
    # Campos de Empréstimo
    nome_solicitante = forms.CharField(required=False, label="Nome do Solicitante", widget=forms.TextInput(attrs={'class': 'form-control'}))
    contato = forms.CharField(required=False, label="Contato / Whatsapp", widget=forms.TextInput(attrs={'class': 'form-control'}))
    data_prevista = forms.DateField(required=False, label="Previsão de Devolução", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        is_emprestimo = cleaned_data.get('is_emprestimo')
        
        if is_emprestimo:
            if not cleaned_data.get('nome_solicitante'):
                self.add_error('nome_solicitante', "Nome do solicitante é obrigatório para empréstimos.")
            if not cleaned_data.get('data_prevista'):
                self.add_error('data_prevista', "Data prevista de devolução é obrigatória.")
        
        return cleaned_data
