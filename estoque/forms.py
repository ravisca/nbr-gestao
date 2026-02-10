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
