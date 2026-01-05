from django.contrib import admin
from .models import Beneficiario

@admin.register(Beneficiario)
class BeneficiarioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'telefone', 'ativo')
    search_fields = ('nome_completo', 'cpf')
    list_filter = ('genero', 'ativo')