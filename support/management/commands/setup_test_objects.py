from shared.utils import SetupObjects
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    
    help = "Sets up test objects."

    def handle(self, *args, **kwargs):
        
        test_objects = SetupObjects()
        test_objects.create_test_objects()
        self.stdout.write(self.style.SUCCESS('Object successfully created.'))
