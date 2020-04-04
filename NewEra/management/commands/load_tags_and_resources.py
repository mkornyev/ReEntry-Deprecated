from django.core.management.base import BaseCommand
from NewEra.models import Resource, Tag
import csv
import re

# POPULATE SCRIPT

class Command(BaseCommand):
    args = '<this func takes no args>'
    help = 'Run this script to create the resources and tags.'

    def _create_tags_and_resources(self):
        tags = set()

        with open('Northside PD Service Providers.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            header = next(reader, None)
            for row in reader:
                tags.add(row[1])

                tag = Tag.objects.all().filter(name=row[1]).first()
                if (tag == None):
                    tag = Tag.objects.create(name=row[1])
                    tag.save()

                phone_formatted = row[5].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')

                phone_list = phone_formatted.split('ext.')
                if len(phone_list) > 1:
                    phone_extension = phone_list[1]
                else:
                    phone_extension = ''

                phone_formatted = ''.join(list(filter(str.isdigit, phone_list[0])))

                print(phone_formatted + ' + ' + phone_extension)

                r = Resource.objects.create(name=row[0], url=row[2], contact_name=row[3], contact_position=row[4], phone=phone_formatted, extension=phone_extension, fax_number=row[6], contact_email=row[7], email=row[7], street=row[8], city=row[9], state=row[10], zip_code=row[11], street_secondary=row[12], description=row[13])
                r.tags.add(tag)
                r.save()

                print(tag.name + " + " + r.name)

            '''
            for tag in tags:
                t.save()
                # print(tag)
                # print(', '.join(row))
            '''
            

        '''
        sow = User.objects.create_user(username='sow', password='sow', first_name='Max', last_name='K', email='mkornyev@gmail.com')
        sow.is_staff = True 
        sow.is_superuser = False
        sow.save()

        admin = User.objects.create_user(username='admin', password='admin', first_name='Taili', last_name='T', email='admin@gmail.com')
        admin.is_staff = True 
        admin.is_superuser = True
        admin.save()

        print("\nAdmin and SOW users created.\n")
        '''

        print("Resources loaded from CSV")

    def handle(self, *args, **options):
        self._create_tags_and_resources()