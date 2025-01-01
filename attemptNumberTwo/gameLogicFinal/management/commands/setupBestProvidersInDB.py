from django.core.management.base import BaseCommand
from csvFileParser.models import game, streaming_package, streaming_offer, clubs, BestStreamingProvider
from django.db.models import Q

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        clubs_list = clubs.objects.all()

        for club in clubs_list:
            # Fetch all games for the club (either as home or away)
            games_for_club = game.objects.filter(Q(team_home=club.name) | Q(team_away=club.name))

            # Find all streaming offers that cover these games
            streaming_offers = streaming_offer.objects.filter(game_id__in=games_for_club)
            if not streaming_offers.exists():
                self.stdout.write(f"No streaming offers available for {club.name}.")
                continue

            # Aggregate packages and calculate the total coverage and cost
            package_coverage = {}
            for offer in streaming_offers:
                package_id = offer.streaming_package_id.id
                if package_id not in package_coverage:
                    package_coverage[package_id] = {
                        'covered_games': set(),
                        'total_cost': 0,
                    }
                package_coverage[package_id]['covered_games'].add(offer.game_id.id)

                # Calculate cost using yearly subscription price if available, else monthly price
                package = offer.streaming_package_id
                cost = package.monthly_price_yearly_subscription_in_cents or package.monthly_price_cents
                package_coverage[package_id]['total_cost'] = cost

            # Find the package with the lowest cost and 100% coverage, or the one with the most coverage
            best_package = None
            min_cost = float('inf')
            max_coverage = 0
            total_games = set(games_for_club.values_list('id', flat=True))

            for package_id, data in package_coverage.items():
                coverage = len(data['covered_games'])

                if data['covered_games'] == total_games:
                    # Prioritize 100% coverage with the lowest cost
                    if data['total_cost'] < min_cost:
                        best_package = package_id
                        min_cost = data['total_cost']
                else:
                    # Otherwise, find the package with the most coverage
                    if coverage > max_coverage or (coverage == max_coverage and data['total_cost'] < min_cost):
                        best_package = package_id
                        max_coverage = coverage
                        min_cost = data['total_cost']

            # Update or create BestStreamingProvider record for the club
            if best_package:
                best_streaming_package = streaming_package.objects.get(id=best_package)
                BestStreamingProvider.objects.update_or_create(
                    club=club,
                    defaults={
                        'streaming_package': best_streaming_package,
                        'is_best_provider': True
                    }
                )
                self.stdout.write(f"Assigned {best_streaming_package.name} as the best provider for {club.name}")
            else:
                self.stdout.write(f"No suitable streaming package found for {club.name}")

        self.stdout.write(self.style.SUCCESS('Best streaming providers assigned!'))
