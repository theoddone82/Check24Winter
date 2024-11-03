
from django.core.management.base import BaseCommand
from csvFileParser.models import game , streaming_package, streaming_offer, clubs, lieges
from django.db.models import Q

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Fetch distinct category values from Book
        liegeList = lieges.objects.all()
        print(liegeList)
        for liege in liegeList:
            liege.score = 0
            name = liege.name
            games = game.objects.filter(Q(tournament_name=name))
            packages = streaming_offer.objects.filter(game_id__in=games)
            liege.score =len(packages)
            print(liege.score)
            print(name)
            liege.save()
            
            

        self.stdout.write(self.style.SUCCESS('Score calculated!'))