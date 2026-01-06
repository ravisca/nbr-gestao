from django.contrib import admin
from django.utils import timezone
from .models import Projeto, TipoAtividade, RegistroAtividade

# --- CORREÇÃO: Registramos o TipoAtividade individualmente ---
@admin.register(TipoAtividade)
class TipoAtividadeAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'projeto__nome'] 
    list_display = ('nome', 'projeto')

class TipoAtividadeInline(admin.TabularInline):
    model = TipoAtividade
    extra = 1

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')
    inlines = [TipoAtividadeInline]

@admin.register(RegistroAtividade)
class RegistroAtividadeAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'tipo_atividade', 'data', 'monitor')
    list_filter = ('projeto', 'data')

    def get_changeform_initial_data(self, request):
            initial = super().get_changeform_initial_data(request)
            initial['monitor'] = request.user.pk
            initial['data'] = timezone.now().date()
            
            return initial

    def save_model(self, request, obj, form, change):
        if not obj.monitor_id:
            obj.monitor = request.user
        super().save_model(request, obj, form, change)

    fieldsets = (
        ('Seleção', {
            'fields': ('projeto', 'tipo_atividade', 'data', 'monitor')
        }),
        ('Relato', {
            'fields': ('descricao',)
        }),
        ('Fotos (1 a 4)', {
            'fields': ('foto_1', 'foto_2', 'foto_3', 'foto_4')
        }),
        ('Vídeos (1 a 2)', {
            'fields': ('video_1', 'video_2')
        }),
    )

    class Media:
        js = ('atividades/js/admin_filtro_projeto.js',)