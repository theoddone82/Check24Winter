from django.shortcuts import render, redirect
from django.urls import reverse

from gameLogic.forms import footballTeamForm
from csvFileParser.models import game, streaming_package, streaming_offer, clubs, lieges
from django.db.models.functions import Coalesce
import json
from django.core.cache import cache
from django.views.decorators.cache import cache_page
import hashlib
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, F, Q, FloatField
from django.db.models.functions import Coalesce, NullIf
from django.core.exceptions import BadRequest



def generate_cache_key(selected_clubs, selected_lieges):
    # Combine the lists and sort them to ensure consistent order
    key_data = {
        'clubs': sorted(selected_clubs),
        'lieges': sorted(selected_lieges)
    }
    # Convert to JSON string
    key_string = json.dumps(key_data)
    # Create a hash of the string
    key_hash = hashlib.md5(key_string.encode('utf-8')).hexdigest()
    # Prefix the key to avoid conflicts
    cache_key = f'streaming_table_{key_hash}'
    return cache_key

def streaming_table(request):
    return render(request,'all_selection-v3.html')

def homepage(request):
    return render(request, 'homepage.html')


def display_table(request):
    if request.method == "POST":
        selectedClubs = request.POST.getlist('clubs') 
        selectedLieges = request.POST.getlist('lieges') 
        cache_key = generate_cache_key(selectedClubs, selectedLieges)
        context = cache.get(cache_key)
        if context and False:
            return render(request, 'result-v3.html', context)
        
        # Fetch liege names if any are selected
        if selectedLieges:
            lieges_but_not_db = lieges.objects.filter(id__in=selectedLieges).values_list('name', flat=True).order_by('-score')
        else:
            lieges_but_not_db = set()

        # Fetch clubs; if none selected, fetch all
        if selectedClubs:
            clubList = clubs.objects.filter(id__in=selectedClubs)
        else:
            clubList = clubs.objects.all()

        club_names = clubList.values_list('name', flat=True)

        # Fetch games involving selected clubs and lieges
        games_query = Q(team_home__in=club_names) | Q(team_away__in=club_names)
        if lieges_but_not_db:
            games_query &= Q(tournament_name__in=lieges_but_not_db)

        games = game.objects.filter(games_query).values('id', 'tournament_name')
        game_ids = [game['id'] for game in games]
        tournament_names = set(game['tournament_name'] for game in games)

        # Fetch streaming offers
        streaming_offers = streaming_offer.objects.filter(
            game_id__in=game_ids
        ).select_related('streaming_package_id', 'game_id')

        # Get unique package IDs
        unique_package_ids = streaming_offers.values_list('streaming_package_id', flat=True).distinct()

        # Annotate packages with calculated fields
        packages_qs = streaming_package.objects.filter(id__in=unique_package_ids).annotate(
            monthly_price_cents_float=Case(
                When(monthly_price_cents__isnull=True, then=Value(None)),
                When(monthly_price_cents=0, then=Value(0.0)),
                default=F('monthly_price_cents') / 100.0,
                output_field=FloatField()
            ),
            monthly_price_yearly_subscription_in_cents_float=Case(
                When(monthly_price_yearly_subscription_in_cents__isnull=True, then=Value(None)),
                When(monthly_price_yearly_subscription_in_cents=0, then=Value(0.0)),
                default=F('monthly_price_yearly_subscription_in_cents') / 100.0,
                output_field=FloatField()
            )
        )

        # Build package data and mappings
        packages = []
        package_info = {}
        for pak in packages_qs:
            package_data = {
                'id': pak.id,
                'name': pak.name,
                'logo': 'nologo.png',  # or pak.logo if you have it
                'monthly_price_cents': pak.monthly_price_cents_float,
                'monthly_price_yearly_subscription_in_cents': pak.monthly_price_yearly_subscription_in_cents_float,
            }
            packages.append(package_data)
            package_info[pak.id] = package_data

        # Build availability dictionary
        availability = {}
        for off in streaming_offers:
            package_id = off.streaming_package_id.id
            tournament_name = off.game_id.tournament_name

            if package_id not in availability:
                availability[package_id] = {}

            if tournament_name not in availability[package_id]:
                availability[package_id][tournament_name] = {'live': False, 'highlight': False}

            # OR both live/highlights
            availability[package_id][tournament_name]['live'] |= bool(off.live)
            availability[package_id][tournament_name]['highlight'] |= bool(off.highlights)

        # If no lieges were selected, use the tournaments from the games
        if not lieges_but_not_db:
            lieges_but_not_db = tournament_names

        # Build package coverage mapping
        package_coverage = {}
        for package_id, tournaments in availability.items():
            coverage = set()
            for tournament_name, data in tournaments.items():
                # Change the coverage rule if you want live OR highlights
                if data.get('live') or data.get('highlight'):
                    coverage.add(tournament_name)
            package_coverage[package_id] = coverage

        # Required tournaments (leagues)
        required_tournaments = set(tournament_names)

        # Greedy algorithm for best budget coverage
        selected_packages = set()
        remaining_tournaments = set(required_tournaments)
        while remaining_tournaments:
            best_package = None
            best_coverage = set()
            best_cost_per_tournament = float('inf')

            for package_id, coverage in package_coverage.items():
                if package_id in selected_packages:
                    continue
                new_coverage = coverage & remaining_tournaments
                if not new_coverage:
                    continue

                cost = package_info[package_id]['monthly_price_yearly_subscription_in_cents']
                if cost is None:
                    cost = 0.0  # treat None cost as 0 or handle differently
                if cost == 0:
                    cost = 0.01  # to avoid division by zero
                cost_per_tournament = cost / len(new_coverage)

                if cost_per_tournament < best_cost_per_tournament:
                    best_package = package_id
                    best_coverage = new_coverage
                    best_cost_per_tournament = cost_per_tournament

            if not best_package:
                # We couldn't find any package that covers remaining tournaments
                break

            selected_packages.add(best_package)
            remaining_tournaments -= best_coverage

        packages_as_objects = streaming_package.objects.filter(
            id__in=selected_packages
        ).annotate(
            monthly_price_cents_float=Coalesce(NullIf(F('monthly_price_cents'), 0) / 100.0, Value(None)),
            monthly_price_yearly_subscription_in_cents_float=Coalesce(NullIf(F('monthly_price_yearly_subscription_in_cents'), 0) / 100.0, Value(None))
        )

        # ---------------------------
        # Add coverage status flags
        # ---------------------------
        all_covered = (len(remaining_tournaments) == 0)
        any_covered = len(selected_packages) > 0

        if all_covered:
            partial_coverage = False
        elif any_covered:
            partial_coverage = True  # some coverage but not all
        else:
            partial_coverage = False  # no coverage at all

        context = {
            'packages': packages,
            'leagues': lieges_but_not_db,
            'availability': availability,
            'selected_packages2': packages_as_objects,
            'selected_packages': selected_packages,
            'all_covered': all_covered,
            'partial_coverage': partial_coverage,
        }
        cache.set(cache_key, context, timeout=None)
        return render(request, 'result-v3.html', context)
    else:
        return redirect(reverse('homepage'))
