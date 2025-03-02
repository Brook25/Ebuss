from shared.utils import SetupObjects
from django.management.base import BaseCommand


class SetupObjs(BaseCommand):
    
    help = "Sets up test objects."

    def handle(self, *args, **kwargs):
        
        test_objects = SetupObjects()
        test_objects.create_test_objects()
        self.stdout.write(self.style.success('Object successfully created.'))
