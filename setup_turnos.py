import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from beneficiarios.models import Turno

turnos_padrao = ["Manhã", "Tarde", "Noite", "Integral"]

print("--- Configurando Turnos Padrão ---")
for nome in turnos_padrao:
    obj, created = Turno.objects.get_or_create(nome=nome)
    if created:
        print(f"[+] Criado: {nome}")
    else:
        print(f"[=] Já existe: {nome}")

print("--- Concluído ---")
