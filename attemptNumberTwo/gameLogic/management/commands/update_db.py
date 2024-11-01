
from django.core.management.base import BaseCommand
from csvFileParser.models import game , streaming_package, streaming_offer, clubs, lieges

class Command(BaseCommand):
    help = 'Populates UniqueCategory table with distinct categories from Book'

    def handle(self, *args, **kwargs):
        # Fetch distinct category values from Book
        games = game.objects.values_list('team_home', flat=True).distinct()

        for g in games:
            # Create UniqueCategory records if they don't exist
            clubs.objects.get_or_create(name=g)
        
        self.stdout.write(self.style.SUCCESS('UniqueCategory table populated with distinct categories!'))