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
            print(name)
            # Look for games where the club is the home team
            games = game.objects.filter(Q(team_home=name) | Q(team_away=name))
            for g in games:
                print(f"gameid: {g.id}")
                temp = streaming_offer.objects.filter(game_id=g.id)
                for t in temp:
                    print(f" {g.tournament_name} streaming offers {t.live} || {t.highlights}")
                    # if t.live and t.highlights:
                    streaming_packages.append(t.streaming_package_id.id)
                    test[f"{g.tournament_name}"] = {  # Adding the game with parameters
                        "live": f"{t.live}",
                        "highlights": f"{t.highlights}"
                    }
        associated_lieges = games.values_list('tournament_name', flat=True).distinct()
        print(test)
        unique_package_ids = list(set(streaming_packages))
        packages = streaming_package.objects.filter(id__in=unique_package_ids)
        tournaments = game.objects.values_list('tournament_name', flat=True).distinct()

        enriched_packages = []
        for pak in packages:

            # Add additional parameters to each package dictionary
            enriched_package = {
                'name': pak.name,
                'monthly_price_cents': pak.monthly_price_cents,
                'monthly_price_yearly_subscription_in_cents': pak.monthly_price_yearly_subscription_in_cents,
                
            }

            enriched_packages.append(enriched_package)
                # for gam in games: 
                #     print(gam)
        for lig in associated_lieges:
            print(lig)
        # Pass enriched packages to the template
        return render(request, 'display_table.html', {'data': enriched_packages})
    
    else:
        form = footballTeamForm.TeamSelectionForm()
        print(form)
        return render(request, 'index.html', {'form': form})