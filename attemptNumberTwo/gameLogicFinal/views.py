from django.shortcuts import render, redirect
from django.urls import reverse

from django.http import JsonResponse

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
    return render(request,'final_select.html')

def homepage(request):
    return render(request, 'homepage.html')


def display_table(request):
    if request.method == "POST":
        selectedClubs = request.POST.getlist('clubs') 
        selectedLieges = request.POST.getlist('lieges') 

        if selectedLieges:
            selected_lieges = lieges.objects.filter(id__in=selectedLieges).values_list('name', flat=True).order_by('-score')
        else:
            selected_lieges = set()

        # Fetch clubs; if none selected, fetch all
        if selectedClubs:
            clubList = clubs.objects.filter(id__in=selectedClubs)
        else:
            clubList = clubs.objects.all()

        club_names = clubList.values_list('name', flat=True)

        print(club_names)
        # find all games associated with lieges

        games_query = Q(team_home__in=club_names) | Q(team_away__in=club_names)
        if selected_lieges:
            games_query &= Q(tournament_name__in=selected_lieges)

        games = game.objects.filter(games_query).values('id', 'tournament_name', 'starts_at')
        game_ids = [game['id'] for game in games]

        streaming_packages = streaming_package.objects.all()
        for package in streaming_packages:
            offers = streaming_offer.objects.filter(
                game_id__in=game_ids,
                streaming_package_id=package.id
            ).values('game_id', 'live', 'highlights')
            print(offers)

        return JsonResponse({
            'streaming_packages': list(streaming_packages.values('name', 'monthly_price_cents', 'monthly_price_yearly_subscription_in_cents'))
        })
