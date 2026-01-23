
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from atividades.models import RegistroAtividade, Projeto

def setup_groups():
    # Create or get groups
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    professor_group, _ = Group.objects.get_or_create(name='Professor')

    # Assign permissions
    # Professor needs to add RegistroAtividade and view Projects
    
    # Get content types
    ct_registro = ContentType.objects.get_for_model(RegistroAtividade)
    ct_projeto = ContentType.objects.get_for_model(Projeto)

    # Permissions for Professor
    prof_perms = [
        Permission.objects.get(content_type=ct_registro, codename='add_registroatividade'),
        Permission.objects.get(content_type=ct_registro, codename='view_registroatividade'),
        Permission.objects.get(content_type=ct_projeto, codename='view_projeto'),
        Permission.objects.get(content_type=ct_projeto, codename='change_projeto'), # Assuming they might edit? user said "gestao" (management)
        Permission.objects.get(content_type=ct_projeto, codename='add_projeto'),
    ]
    
    for perm in prof_perms:
        professor_group.permissions.add(perm)

    print("Groups 'Admin' and 'Professor' configured successfully.")

if __name__ == '__main__':
    setup_groups()
