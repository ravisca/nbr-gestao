from django.contrib import admin
from .models import Beneficiario

@admin.register(Beneficiario)
class BeneficiarioAdmin(admin.ModelAdmin):
    # As colunas que vão aparecer na tabela de listagem
    list_display = ('id', 'nome_completo', 'projeto', 'idade', 'eh_maior_idade', 'contato', 'status', 'data_cadastro')
    
    # Filtros laterais
    list_filter = ('projeto', 'turno', 'status', 'data_cadastro')
    
    # Barra de busca
    search_fields = ('nome_completo', 'cpf', 'responsavel')
    
    # Organização visual do formulário de cadastro (Agrupando campos)
    fieldsets = (
        ('Identificação', {
            'fields': ('nome_completo', 'cpf', 'data_nascimento', 'contato')
        }),
        ('Saúde & Acessibilidade', {
            'fields': ('quadro_saude', 'necessita_acessibilidade')
        }),
        ('Vínculo com a ONG', {
            'fields': ('projeto', 'atividade', 'turno', 'status')
        }),
        ('Responsável (Se menor)', {
            'fields': ('responsavel', 'grau_parentesco')
        }),
        ('Outros', {
            'fields': ('observacoes',)
        }),
    )