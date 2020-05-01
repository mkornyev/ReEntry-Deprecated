from django.core.management.base import BaseCommand
from NewEra.models import Resource, Tag
import csv
import re

# POPULATE SCRIPT

class Command(BaseCommand):
    args = '<this func takes no args>'
    help = 'Run this script to create the resources and tags.'

    def _create_tags_and_resources(self):

        with open('Northside PD Service Providers.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            header = next(reader, None)
            for row in reader:

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
                fax_formatted = row[6].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')

                r = Resource.objects.create(name=row[0], url=row[2], contact_name=row[3], contact_position=row[4], phone=phone_formatted, extension=phone_extension, fax_number=fax_formatted, contact_email=row[7], email=row[7], street=row[8], city=row[9], state=row[10], zip_code=row[11], street_secondary=row[12], description=row[13])
                r.tags.add(tag)
                r.save()

        print("Resources loaded from CSV.")

    def handle(self, *args, **options):
        self._create_tags_and_resources()
