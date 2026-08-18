
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from atividades.models import RegistroAtividade, Projeto

def setup_groups():
    # Create or get groups
    admin_group, _ = Group.objects.get_or_create(name='Gestão')
    professor_group, _ = Group.objects.get_or_create(name='Núcleo')
    operacional_group, _ = Group.objects.get_or_create(name='Operacional')

    # Assign permissions
    # Professor needs to add RegistroAtividade and view Projects
    
    # Get content types
    ct_registro = ContentType.objects.get_for_model(RegistroAtividade)
    ct_projeto = ContentType.objects.get_for_model(Projeto)

    # Permissions for Professor (Núcleo)
    # Núcleo pode registrar atividades e visualizar projetos (para selecionar no formulário)
    # NÃO pode criar ou editar projetos — isso é função da Gestão
    prof_perms = [
        Permission.objects.get(content_type=ct_registro, codename='add_registroatividade'),
        Permission.objects.get(content_type=ct_registro, codename='view_registroatividade'),
        Permission.objects.get(content_type=ct_projeto, codename='view_projeto'),
    ]
    
    for perm in prof_perms:
        professor_group.permissions.add(perm)

    # Permissions for Operacional (view Project)
    operacional_group.permissions.add(
        Permission.objects.get(content_type=ct_projeto, codename='view_projeto')
    )

    print("Groups 'Gestão', 'Núcleo' and 'Operacional' configured successfully.")

if __name__ == '__main__':
    setup_groups()
