from django.contrib import admin
from .models import Beneficiario, Turno

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Beneficiario)
class BeneficiarioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'projeto', 'idade', 'eh_maior_idade', 'telefone', 'status')
    list_filter = ('projeto', 'turno', 'status')
    search_fields = ('nome_completo', 'cpf')

    fieldsets = (
        ('Identificação', {
            'fields': ('nome_completo', 'cpf', 'data_nascimento', 'telefone')
        }),
        ('Saúde', {
            'fields': ('tem_problema_saude', 'descricao_saude')
        }),
        ('Acessibilidade', {
            'fields': ('necessita_acessibilidade', 'descricao_acessibilidade')
        }),
        ('Vínculo', {
            'fields': ('projeto', 'atividade', 'turno', 'status')
        }),
        ('Dados do Responsável (Obrigatório para menores de 18)', {
            'classes': ('responsavel-group',),
            'fields': ('responsavel', 'grau_parentesco')
        }),
        ('Outros', {
            'fields': ('observacoes',)
        }),
    )

    class Media:
        js = ('beneficiarios/js/admin_script.js',)