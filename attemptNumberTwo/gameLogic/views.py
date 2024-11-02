from django.shortcuts import render,redirect
from django.urls import reverse
from .forms import selects, footballTeamForm
from csvFileParser.models import game, streaming_package, streaming_offer, clubs, lieges
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.
def index(request):
    if request.method == "POST":
        selectedClubs = request.POST.getlist('clubs')

        test={}
        streaming_packages = []
        for option in selectedClubs:
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

            enriched_packages.append(enriched_package)
        # Pass enriched packages to the template
        return render(request, 'display_table.html', {'data': enriched_packages})
    
    else:
        form = footballTeamForm.TeamSelectionForm()
        return render(request, 'index.html', {'form': form})
    

def streaming_table(request):
    # Placeholder data structure to simulate database fetching
        
    if request.method == "POST":
        streaming_packages = []
        test={}
        selectedClubs = request.POST.getlist('clubs')

        if selectedClubs == []:
            return redirect(reverse('index'))
        print(selectedClubs)
        lieges = set()
        for name in clubs.objects.filter(id__in=selectedClubs):
            games = game.objects.filter(Q(team_home=name) | Q(team_away=name))
            for g in games:
                lieges.add(g.tournament_name)
                temp = streaming_offer.objects.filter(game_id=g.id)
                for t in temp:
                    # if t.live and t.highlights:
                    streaming_packages.append(t.streaming_package_id.id)
                    test[f"{g.tournament_name}"] = {  # Adding the game with parameters
                        "live": f"{t.live}",
                        "highlights": f"{t.highlights}"
                    }       

        packages = [
            # {'id': 1, 'name': 'MegaSport', 'logo': 'megasport_logo.png','monthly_price_cents': 1000, 'monthly_price_yearly_subscription_in_cents': 9000},
            # {'id': 2, 'name': 'Prime Video', 'logo': 'prime_video_logo.png','monthly_price_cents': 1000, 'monthly_price_yearly_subscription_in_cents': 9000},
            # {'id': 3, 'name': 'Premium', 'logo': 'premium_logo.png','monthly_price_cents': 1000, 'monthly_price_yearly_subscription_in_cents': 9000},
            # {'id': 4, 'name': 'Perfect Plus', 'logo': 'perfect_plus_logo.png', 'monthly_price_cents': 1000, 'monthly_price_yearly_subscription_in_cents': 9000},
            # Add more packages as needed
        ]
        unique_package_ids = list(set(streaming_packages))
        p = streaming_package.objects.filter(id__in=unique_package_ids)

        print(len(lieges))
        print(len(games))

        for pak in p:
            packages.append({'id': pak.id, 'name': pak.name, 'logo': 'nologo.png', 'monthly_price_cents': pak.monthly_price_cents / 100.0 if pak.monthly_price_cents else pak.monthly_price_cents, 'monthly_price_yearly_subscription_in_cents': pak.monthly_price_yearly_subscription_in_cents / 100.0 if pak.monthly_price_yearly_subscription_in_cents else pak.monthly_price_yearly_subscription_in_cents,})
            
        availability = {
            # 1: {'DFB Pokal 24/25': {'live': True, 'highlight': True},
            #     'Serie A 24/25': {'live': True, 'highlight': False}},
            # 3: {'Bundesliga 23/24': {'live': True, 'highlight': True},
            #     'Serie A 24/25': {'live': True, 'highlight': False}},
            # 2: {'La Liga': {'live': True, 'highlight': True},
            #     '2. BL': {'live': False, 'highlight': False}},
            # 5: {'La Liga': {'live': False, 'highlight': True},
            #     '2. BL': {'live': False, 'highlight': False}},
            # 4: {'La Liga': {'live': True, 'highlight': True},
            #     '2. BL': {'live': False, 'highlight': False}},
            # Add more package and league combinations as needed
        }

        for off in streaming_offer.objects.filter(Q(streaming_package_id__in=p) & Q(game_id__in=games)):
            package_id = off.streaming_package_id.id
            tournament_name = off.game_id.tournament_name

            # Initialize the package entry if it doesn't exist
            if package_id not in availability:
                availability[package_id] = {}

            # Update or set the tournament entry with live and highlight data
            availability[package_id][tournament_name] = {
                'live': off.live if off.live is not None else False,
                'highlight': off.highlights if off.highlights is not None else False
            }
        context = {
            'packages': packages,
            'leagues': lieges,
            'availability': availability
        }
        
        return render(request, 'streaming_table.html', context)

    else:
        form = footballTeamForm.TeamSelectionForm()
        return render(request, 'index.html', {'form': form})
    