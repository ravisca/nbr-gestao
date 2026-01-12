import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from financeiro.models import CategoriaReceita
from estoque.models import UnidadeMedida
from beneficiarios.models import Turno

def populate():
    # Financeiro
    cats = ['Doação', 'Venda de Bazar', 'Evento', 'Verba/Convênio', 'Outro']
    for nome in cats:
        CategoriaReceita.objects.get_or_create(nome=nome)
    print("Categorias Financeiras criadas.")

    # Estoque
    unidades = [
        ('UN', 'Unidade'),
        ('KG', 'Quilograma'),
        ('LT', 'Litro'),
        ('CX', 'Caixa'),
        ('PCT', 'Pacote')
    ]
    for sigla, nome in unidades:
        UnidadeMedida.objects.get_or_create(sigla=sigla, defaults={'nome': nome})
    print("Unidades de Medida criadas.")

    # Beneficiarios
    turnos = ['Manhã', 'Tarde', 'Noite', 'Integral']
    for nome in turnos:
        Turno.objects.get_or_create(nome=nome)
    print("Turnos criados.")

if __name__ == '__main__':
    populate()
