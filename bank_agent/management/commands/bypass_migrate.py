from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Bypass migrations - do nothing'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Migrations bypassed - no database needed'))