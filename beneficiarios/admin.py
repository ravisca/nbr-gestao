from django.contrib import admin
from .models import Beneficiario, Turno, VinculoBeneficiario

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

class VinculoInline(admin.TabularInline):
    model = VinculoBeneficiario
    extra = 1

@admin.register(Beneficiario)
class BeneficiarioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'idade', 'eh_maior_idade', 'telefone', 'status')
    list_filter = ('status',)
    search_fields = ('nome_completo', 'cpf')
    inlines = [VinculoInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('nome_completo', 'cpf', 'data_nascimento', 'telefone', 'foto')
        }),
        ('Saúde', {
            'fields': ('tem_problema_saude', 'descricao_saude')
        }),
        ('Acessibilidade', {
            'fields': ('necessita_acessibilidade', 'descricao_acessibilidade')
        }),
        ('Dados do Responsável (Obrigatório para menores de 18)', {
            'classes': ('responsavel-group',),
            'fields': ('responsavel', 'grau_parentesco')
        }),
        ('Outros', {
            'fields': ('observacoes', 'status')
        }),
    )

    class Media:
        js = ('beneficiarios/js/admin_script.js',)