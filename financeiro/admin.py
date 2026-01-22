from django.contrib import admin
from django.utils.html import format_html
from .models import Conta, Receita, Despesa

@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'saldo_formatado')
    readonly_fields = ('saldo_atual',)

    def saldo_formatado(self, obj):
        return f"R$ {obj.saldo_atual:,.2f}"

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('data', 'categoria', 'valor', 'conta', 'descricao')
    list_filter = ('data', 'categoria', 'conta')
    
    def save_model(self, request, obj, form, change):
        if not obj.responsavel_id: obj.responsavel = request.user
        super().save_model(request, obj, form, change)

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    # A lista exibe os campos principais para conferência rápida
    list_display = ('id', 'data_emissao', 'razao_social', 'nota_fiscal', 'projeto', 'rubrica', 'valor_formatado', 'ver_nota')
    
    # Filtros poderosos para achar notas específicas
    list_filter = ('projeto', 'mes_referencia', 'ano_referencia', 'rubrica', 'conta')
    
    search_fields = ('razao_social', 'cnpj', 'nota_fiscal', 'observacoes')
    
    # Navegação por data
    date_hierarchy = 'data_emissao'

    def valor_formatado(self, obj):
        return format_html('<span style="color: red; font-weight: bold;">R$ {:,.2f}</span>', obj.valor)
    valor_formatado.short_description = "Valor"

    def ver_nota(self, obj):
        if obj.comprovante:
            return format_html('<a href="{}" target="_blank">📄 Nota</a>', obj.comprovante.url)
        return "-"
    ver_nota.short_description = "Arquivo"

    def save_model(self, request, obj, form, change):
        if not obj.responsavel_id: obj.responsavel = request.user
        super().save_model(request, obj, form, change)

    # Organização do Formulário igual você pediu
    fieldsets = (
        ('Dados do Pagamento', {
            'fields': ('conta', 'projeto', 'rubrica', 'valor')
        }),
        ('Dados Fiscais (Prestação de Contas)', {
            'fields': ('razao_social', 'cnpj', 'nota_fiscal', 'serie', 'data_emissao', 'comprovante')
        }),
        ('Competência', {
            'fields': ('mes_referencia', 'ano_referencia')
        }),
        ('Extras', {
            'fields': ('observacoes',)
        }),
    )