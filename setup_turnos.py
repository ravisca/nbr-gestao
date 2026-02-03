import os
import django

# Carregar variáveis do .env se não estiverem definidas
if not os.getenv('DB_ENGINE') and os.path.exists('.env'):
    print("--- Carregando variáveis de ambiente do .env ---")
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

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
