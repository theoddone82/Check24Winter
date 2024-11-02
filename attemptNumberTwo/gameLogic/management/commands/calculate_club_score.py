
from django.core.management.base import BaseCommand
from csvFileParser.models import game , streaming_package, streaming_offer, clubs, lieges
from django.db.models import Q

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Fetch distinct category values from Book
        c = clubs.objects.all()
        print(c)
        for club in c:
            club.score = 0
            name = club.name
            games = game.objects.filter(Q(team_home=name) | Q(team_away=name))
            packages = streaming_offer.objects.filter(game_id__in=games)
            club.score =len(packages)
            print(club.score)
            print(name)
            club.save()
        streaming_offer.objects.filter(game_id__team_home=club).count()

            

        self.stdout.write(self.style.SUCCESS('Score calculated!'))