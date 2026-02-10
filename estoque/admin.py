from django.contrib import admin
from django.utils.html import format_html
from datetime import date
from .models import Categoria, UnidadeMedida, Item, Movimentacao, Emprestimo

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ['nome']

@admin.register(UnidadeMedida)
class UnidadeMedidaAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'sigla']
    list_display = ('nome', 'sigla')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'status_estoque', 'quantidade_atual', 'unidade')
    list_filter = ('categoria',)
    search_fields = ('nome',)
    readonly_fields = ('quantidade_atual',)

    def status_estoque(self, obj):
        if obj.quantidade_atual <= obj.estoque_minimo:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ BAIXO ({})</span>', obj.quantidade_atual)
        return format_html('<span style="color: green;">OK ({})</span>', obj.quantidade_atual)
    status_estoque.short_description = "Situação"

@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('data', 'tipo_formatado', 'item', 'quantidade', 'usuario')
    list_filter = ('tipo', 'data')
    autocomplete_fields = ['item']

    def tipo_formatado(self, obj):
        color = 'green' if obj.tipo == 'ENTRADA' else 'red'
        icon = '⬆️' if obj.tipo == 'ENTRADA' else '⬇️'
        return format_html('<span style="color: {};">{} {}</span>', color, icon, obj.get_tipo_display())
    tipo_formatado.short_description = "Tipo"

    def save_model(self, request, obj, form, change):
        if not obj.usuario_id: obj.usuario = request.user
        super().save_model(request, obj, form, change)

@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantidade_emprestada', 'nome_solicitante', 'data_prevista', 'status_devolucao')
    list_filter = ('devolvido', 'data_saida')
    search_fields = ('nome_solicitante', 'cpf_solicitante', 'item__nome')
    autocomplete_fields = ['item'] 

    def status_devolucao(self, obj):
        if obj.devolvido:
            # Lógica visual: Se devolveu tudo (verde), se faltou algo (laranja)
            if obj.quantidade_devolvida and obj.quantidade_devolvida < obj.quantidade_emprestada:
                return format_html('<span style="color: orange;">⚠️ Devolução Parcial ({}/{})</span>', obj.quantidade_devolvida, obj.quantidade_emprestada)
            
            # CORREÇÃO AQUI: Usamos {} para injetar o texto, satisfazendo o Django
            return format_html('<span style="color: green;">{}</span>', "✅ Concluído")
            
        if obj.data_prevista < date.today():
            atraso = (date.today() - obj.data_prevista).days
            return format_html('<span style="color: red; font-weight: bold;">⚠️ ATRASADO ({} dias)</span>', atraso)
        
        # CORREÇÃO AQUI TAMBÉM: Usamos {} para injetar o texto
        return format_html('<span style="color: blue;">{}</span>', "⏳ Em Aberto")
    
    status_devolucao.short_description = "Situação"

    fieldsets = (
        ('Dados do Solicitante', {
            'fields': ('nome_solicitante', 'cpf_solicitante', 'contato', 'endereco')
        }),
        ('O Que Foi Levado?', {
            'fields': ('item', 'quantidade_emprestada', 'data_saida', 'data_prevista')
        }),
        ('Retorno', {
            'fields': ('data_devolucao', 'quantidade_devolvida', 'motivo_falta', 'observacoes')
        }),
    )

    # Conecta o Javascript
    class Media:
        js = ('estoque/js/admin_emprestimo.js',)