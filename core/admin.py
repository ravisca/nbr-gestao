from django.contrib import admin
from .models import ConfiguracaoSite


@admin.register(ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    list_display = ('nome_sistema', 'logo_site_preview', 'logo_relatorio_preview', 'favicon_preview')
    fieldsets = (
        (None, {
            'fields': ('nome_sistema', 'logo_site', 'logo_relatorio', 'favicon'),
            'description': 'Configure o nome do sistema e os ícones visuais (logos e favicon).'
        }),
    )

    def logo_site_preview(self, obj):
        if obj.logo_site:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-height: 40px;" />', obj.logo_site.url)
        return "-"
    logo_site_preview.short_description = "Logo Site"

    def logo_relatorio_preview(self, obj):
        if obj.logo_relatorio:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-height: 40px;" />', obj.logo_relatorio.url)
        return "-"
    logo_relatorio_preview.short_description = "Logo Relatório"

    def favicon_preview(self, obj):
        if obj.favicon:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="max-height: 20px;" />', obj.favicon.url)
        return "-"
    favicon_preview.short_description = "Favicon"

    def has_add_permission(self, request):
        # Só permite adicionar se não existir nenhum registro
        return not ConfiguracaoSite.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
