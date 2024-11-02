from django.shortcuts import render,redirect
from django.urls import reverse
from .forms import selects, footballTeamForm
from csvFileParser.models import game, streaming_package, streaming_offer, clubs, lieges
from django.http import HttpResponse
from django.db.models import Q
import time
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
    
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q, F, Value
from django.db.models.functions import Coalesce

def streaming_table(request):
    if request.method == "POST":
        selectedClubs = request.POST.getlist('clubs') 
        selectedLieges = request.POST.getlist('lieges') 

        # Start timing for performance measurement (optional)
        startTime = time.time()

        # Fetch liege names if any are selected
        if selectedLieges:
            lieges_but_not_db = set(
                lieges.objects.filter(id__in=selectedLieges).values_list('name', flat=True)
            )
        else:
            lieges_but_not_db = set()

        # Fetch clubs; if none selected, fetch all
        if selectedClubs:
            clubList = clubs.objects.filter(id__in=selectedClubs)
        else:
            clubList = clubs.objects.all()

        # **Extract club names**
        club_names = clubList.values_list('name', flat=True)

        # **Fetch games involving selected clubs and lieges**
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

        # Fetch packages
        packages_qs = streaming_package.objects.filter(id__in=unique_package_ids).annotate(
            monthly_price_cents_float=Coalesce(F('monthly_price_cents') / 100.0, Value(0.0)),
            monthly_price_yearly_subscription_in_cents_float=Coalesce(F('monthly_price_yearly_subscription_in_cents') / 100.0, Value(0.0))
        )

        # Build packages list
        packages = [
            {
                'id': pak.id,
                'name': pak.name,
                'logo': 'nologo.png',
                'monthly_price_cents': pak.monthly_price_cents_float,
                'monthly_price_yearly_subscription_in_cents': pak.monthly_price_yearly_subscription_in_cents_float,
            }
            for pak in packages_qs
        ]

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

        context = {
            'packages': packages,
            'leagues': lieges_but_not_db,
            'availability': availability
        }

        # End timing and print duration (optional)
        print(f"Total processing time: {time.time() - startTime} seconds")

        return render(request, 'streaming_table.html', context)
    else:
        form = footballTeamForm.TeamSelectionForm()
        return render(request, 'index.html', {'form': form})
