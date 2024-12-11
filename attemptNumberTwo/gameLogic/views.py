from django.shortcuts import render,redirect
from django.urls import reverse
from .forms import selects, footballTeamForm
from csvFileParser.models import game, streaming_package, streaming_offer, clubs, lieges
from django.http import HttpResponse
from django.db.models import Q
import time
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q, F, Value
from django.db.models.functions import Coalesce
from django.core.cache import cache
import time
import hashlib
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, F, FloatField
from django.db.models.functions import Coalesce, NullIf
from django.core.exceptions import BadRequest
from django.core.serializers.json import DjangoJSONEncoder



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
    form = footballTeamForm.TeamSelectionForm()
    return render(request, 'index.html', {'form': form})

def display_table(request):
    if request.method == "POST":
        selectedClubs = request.POST.getlist('clubs') 
        selectedLieges = request.POST.getlist('lieges') 

        # Generate cache key
        cache_key = generate_cache_key(selectedClubs, selectedLieges)
        # Check if the context is in the cache
        context = cache.get(cache_key)
        if context:
            print("Serving from cache")
            return render(request, 'streaming_table.html', context)
        # Start timing for performance measurement (optional)
        startTime = time.time()

        # Fetch liege names if any are selected
        if selectedLieges:
            lieges_but_not_db = lieges.objects.filter(id__in=selectedLieges).values_list('name', flat=True).order_by('-score')# it's a set dumbass order doesn't matter.order_by('-score')
            
        else:
            lieges_but_not_db = set()

        # Fetch clubs; if none selected, fetch all
        if selectedClubs:
            clubList = clubs.objects.filter(id__in=selectedClubs)
        else:
            clubList = clubs.objects.all()

        # Extract club names
        club_names = clubList.values_list('name', flat=True)

        # Fetch games involving selected clubs and lieges
        games_query = Q(team_home__in=club_names) | Q(team_away__in=club_names)
        if lieges_but_not_db:
            games_query &= Q(tournament_name__in=lieges_but_not_db)

        games = game.objects.filter(games_query).values('id', 'tournament_name')
        game_ids = [game['id'] for game in games]
        tournament_names = set(game['tournament_name'] for game in games)

        # Fetch streaming offers for these games
        streaming_offers = streaming_offer.objects.filter(
            game_id__in=game_ids
        ).select_related('streaming_package_id', 'game_id')

        # Get unique package IDs
        unique_package_ids = streaming_offers.values_list('streaming_package_id', flat=True).distinct()
        # Annotate packages with calculated fields
        packages_qs = streaming_package.objects.filter(id__in=unique_package_ids).annotate(
    monthly_price_cents_float=Case(
        When(monthly_price_cents__isnull=True, then=Value(None)),  # If NULL, set to None
        When(monthly_price_cents=0, then=Value(0.0)),              # If 0, set to 0.0
        default=F('monthly_price_cents') / 100.0,                  # Otherwise, calculate float
        output_field=FloatField()
    ),
    monthly_price_yearly_subscription_in_cents_float=Case(
        When(monthly_price_yearly_subscription_in_cents__isnull=True, then=Value(None)),
        When(monthly_price_yearly_subscription_in_cents=0, then=Value(0.0)),
        default=F('monthly_price_yearly_subscription_in_cents') / 100.0,
        output_field=FloatField()
    )
)

        # Build package data and mappings in a single loop
        packages = []
        package_info = {}

        for pak in packages_qs:
            package_data = {
                'id': pak.id,
                'name': pak.name,
                'logo': 'nologo.png',
                'monthly_price_cents': pak.monthly_price_cents_float,
                'monthly_price_yearly_subscription_in_cents': pak.monthly_price_yearly_subscription_in_cents_float,
            }
            # Add package data to both list and dictionary for quick lookup by ID
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
                if data.get('live'):
                    coverage.add(tournament_name)
            package_coverage[package_id] = coverage

        # Required tournaments (leagues)
        required_tournaments = set(tournament_names)

        # Implement greedy algorithm to select best budget packages
        selected_packages = set()

        if selected_packages == set():
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
                        cost = 0  # Assume free
                    if cost == 0:
                        cost = 0.01  # Avoid division by zero
                    cost_per_tournament = cost / len(new_coverage)
                    if cost_per_tournament < best_cost_per_tournament:
                        best_package = package_id
                        best_coverage = new_coverage
                        best_cost_per_tournament = cost_per_tournament

                if not best_package:
                    # Cannot cover remaining tournaments
                    break

                selected_packages.add(best_package)
                remaining_tournaments -= best_coverage
            
        packages_as_objects = streaming_package.objects.filter(id__in=selected_packages).annotate(
            monthly_price_cents_float=Coalesce(NullIf(F('monthly_price_cents'), 0) / 100.0, Value(None)),
            monthly_price_yearly_subscription_in_cents_float=Coalesce(NullIf(F('monthly_price_yearly_subscription_in_cents'), 0) / 100.0, Value(None))
        )
        print(packages_as_objects.values())
        print(packages_as_objects.values_list())
        # Build context
        context = {
            'packages': packages,
            'leagues': lieges_but_not_db,
            'availability': availability,
            'selected_packages2': packages_as_objects,
            'selected_packages': selected_packages,
        }
        print(selected_packages)
        # Cache the context for 10 minutes (600 seconds)
        cache.set(cache_key, context, 600)
        print("succees")
        # End timing and print duration (optional)
        print(f"Total processing time: {time.time() - startTime} seconds")

        return render(request, 'streaming_table.html', context)
    else:
        return BadRequest

def fetch_league_details(request, league_id):
    # Get the league object based on the provided ID
    league = get_object_or_404(league, id=league_id)    
    
    # Prepare the data you want to return
    data = {
        'description': league.description,
        'founded_year': league.founded_year,
        'number_of_teams': league.number_of_teams,
        # add other fields as needed
    }
    
    return JsonResponse(data)

# Create your views here.
def index(request):
    if request.method == "POST":
        selectedClubs = request.POST.getlist('clubs')

        test={}
        streaming_packages = []
        for option in selectedClubs:
            start_time = time.time()
            name = clubs.objects.get(id=option)
            # Look for games where the club is the home team
            games = game.objects.filter(Q(team_home=name) | Q(team_away=name))
            for g in games:
                temp = streaming_offer.objects.filter(game_id=g.id)
                for t in temp:
                    # if t.live and t.highlights:
                    streaming_packages.append(t.streaming_package_id.id)
                    test[f"{g.tournament_name}"] = {  # Adding the game with parameters
                        "live": f"{t.live}",
                        "highlights": f"{t.highlights}"
                    }
        print(time.time() - start_time)
        unique_package_ids = list(set(streaming_packages))
        packages = streaming_package.objects.filter(id__in=unique_package_ids)
        tournaments = game.objects.values_list('tournament_name', flat=True).distinct()

        enriched_packages = []
        for pak in packages:

            # Add additional parameters to each package dictionary
            enriched_package = {
                'name': pak.name,
                'monthly_price_cents': pak.monthly_price_cents / 100.0 if pak.monthly_price_cents else pak.monthly_price_cents,
                'monthly_price_yearly_subscription_in_cents': pak.monthly_price_yearly_subscription_in_cents / 100.0 if pak.monthly_price_yearly_subscription_in_cents else pak.monthly_price_yearly_subscription_in_cents,
            }
            print(time.time() - start_time)

            enriched_packages.append(enriched_package)
        print(time.time() - start_time)


        # Pass enriched packages to the template
        return render(request, 'display_table.html', {'data': enriched_packages})
    
    else:
        form = footballTeamForm.TeamSelectionForm()
        return render(request, 'index.html', {'form': form})
    

def homepage(request):
    return render(request, 'homepage.html')