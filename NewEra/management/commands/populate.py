from django.core.management.base import BaseCommand
from NewEra.models import User
# from blogapp.models import Resource

# POPULATE SCRIPT

class Command(BaseCommand):
    args = '<this func takes no args>'
    help = 'Run this script to create sample users.'

    def _create_users(self):
        sow = User.objects.create_user(username='sow', password='sow', first_name='Max', last_name='K', email='mkornyev@gmail.com')
        sow.is_staff = True 
        sow.is_superuser = False
        sow.save()

        admin = User.objects.create_user(username='admin', password='admin', first_name='Taili', last_name='T', email='admin@gmail.com')
        admin.is_staff = True 
        admin.is_superuser = True
        admin.save()

        print("\nAdmin and SOW users created.\n")

    def handle(self, *args, **options):
        self._create_users()