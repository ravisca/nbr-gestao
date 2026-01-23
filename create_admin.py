
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_admin_user():
    username = 'admin_teste'
    password = '123'
    
    # Create or get user
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(username=username, email='admin@teste.com', password=password)
        print(f"Superuser '{username}' created.")
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"User '{username}' updated.")

    # Assign to group Admin
    try:
        group, _ = Group.objects.get_or_create(name='Admin')
        user.groups.add(group)
        print(f"User '{username}' added to group 'Admin'.")
    except Exception as e:
        print(f"Error adding to group: {e}")

if __name__ == '__main__':
    create_admin_user()
