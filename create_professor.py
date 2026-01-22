
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_test_user():
    username = 'professor_teste'
    password = '123'
    
    # Create or get user
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, password=password)
        print(f"User '{username}' created.")
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"User '{username}' updated.")

    # Assign to group
    try:
        prof_group = Group.objects.get(name='Professor')
        user.groups.add(prof_group)
        print(f"User '{username}' added to group 'Professor'.")
    except Group.DoesNotExist:
        print("Error: Group 'Professor' does not exist. Please run setup_roles.py first.")

if __name__ == '__main__':
    create_test_user()
