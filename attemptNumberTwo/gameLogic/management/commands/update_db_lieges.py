
from django.core.management.base import BaseCommand
from csvFileParser.models import game , streaming_package, streaming_offer, clubs, lieges

class Command(BaseCommand):
    help = 'Populates UniqueCategory table with distinct categories from Book'

    def handle(self, *args, **kwargs):
        # Fetch distinct category values from Book
        temp = game.objects.values_list('tournament_name', flat=True).distinct()

        for liege in temp:
            # Create UniqueCategory records if they don't exist
            lieges.objects.get_or_create(name=liege)
        
        self.stdout.write(self.style.SUCCESS('UniqueCategory table populated with distinct categories!'))