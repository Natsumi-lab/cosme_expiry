"""
List all users in the system.
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cosme_expiry_app.settings')
django.setup()

from django.contrib.auth import get_user_model

def list_users():
    """
    List all users in the system
    """
    User = get_user_model()
    
    print("===== Users in the System =====")
    print(f"Total users: {User.objects.count()}")
    
    for user in User.objects.all():
        print(f"- ID: {user.id}, Username: {user.username}, Email: {user.email}, Is Staff: {user.is_staff}, Is Superuser: {user.is_superuser}")

if __name__ == "__main__":
    list_users()