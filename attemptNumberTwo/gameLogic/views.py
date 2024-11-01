from django.shortcuts import render,redirect
from django.urls import reverse
from .forms import selects, footballTeamForm
from csvFileParser.models import game, streaming_package, streaming_offer, clubs, lieges
from django.http import HttpResponse
# Create your views here.
def index(request):
    if request.method == "POST":
        selectedClubs = request.POST.getlist('clubs')
        print(selectedClubs)
        for option in selectedClubs:
            #get the actuall name not the club id 
            result =  []
            name = clubs.objects.get(id=option)
            print(name)
            # look for games which that club name 
            games = game.objects.filter(team_home=name)
            for g in games:
                print(f"gameid: {g.id}")
                temp = streaming_offer.objects.filter(game_id=g.id)
                for t in temp:
                    print(f" streaming offers {t.live} || {t.highlights}")
                    if t.live and t.highlights:
                        result.append(t.streaming_package_id.id)

        # for res in list(set(result)):
        packages = streaming_package.objects.filter(id__in=result)
        for pak in packages:
            print(pak.monthly_price_yearly_subscription_in_cents)
        return render(request, 'display_table.html', {'data': packages})
    
    else:
        form = footballTeamForm.TeamSelectionForm()
        print(form)
        return render(request, 'index.html', {'form': form})