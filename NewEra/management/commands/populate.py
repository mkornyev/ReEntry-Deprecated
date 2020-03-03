from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
# from blogapp.models import Resource

# POPULATE SCRIPT

class Command(BaseCommand):
    args = '<this func takes no args>'
    help = 'Run this script to create sample users.'

    def _create_users(self):
        sow = User(username='sow', first_name='Max', last_name='K', email='mkornyev@gmail.com', password='sow')
        sow.is_staff = True 
        sow.is_superuser = False
        sow.save()

        admin = User(username='admin', first_name='Taili', last_name='T', email='admin@gmail.com', password='admin')
        admin.is_staff = True 
        admin.is_superuser = True
        admin.save()

    def handle(self, *args, **options):
        self._create_users()