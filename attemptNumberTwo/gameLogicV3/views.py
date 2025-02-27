from django.shortcuts import render, redirect
from django.urls import reverse
from collections import defaultdict

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


def homepage(request):
    return render(request, 'homepage.html')

def dt(request):
    if request.method != "POST":
        return redirect(reverse('homepage'))
    
    # 1. Retrieve selected clubs and lieges from the POST data
    selected_clubs = request.POST.getlist('clubs')
    selected_lieges = request.POST.getlist('lieges')
    
    # 2. Cache logic
    cache_key = generate_cache_key(selected_clubs, selected_lieges)
    context = cache.get(cache_key)
    # For demo, we skip the cache:
    if context and False:
        return render(request, 'result-v3.html', context)

    # 3. Gather league names (lieges) and clubs
    if selected_lieges:
        selected_lieges_names = list(
            lieges.objects.filter(id__in=selected_lieges)
                          .order_by('-score')
                          .values_list('name', flat=True)
        )
    else:
        selected_lieges_names = []

    if selected_clubs:
        club_qs = clubs.objects.filter(id__in=selected_clubs)
    else:
        club_qs = clubs.objects.all()
    club_names = list(club_qs.values_list('name', flat=True))

    # -----------------------------------------------------------------
    # 4. Build a union (OR) query for games
    # -----------------------------------------------------------------
    games_query = Q()
    
    if club_names:
        club_query = Q(team_home__in=club_names) | Q(team_away__in=club_names)
        games_query |= club_query

    if selected_lieges_names:
        liege_query = Q(tournament_name__in=selected_lieges_names)
        games_query |= liege_query

    # If user selected nothing, fetch all or none
    if not club_names and not selected_lieges_names:
        games_query = Q()  # means fetch all

    # 5. Fetch relevant games **including starts_at** for date calculations
    games_qs = game.objects.filter(games_query).values(
        'id', 'tournament_name', 'starts_at'
    )

    # Convert to list so we can iterate multiple times
    games = list(games_qs)
    if not games:
        # If no relevant games, return an empty table or handle differently
        return render(request, 'result-v3.html', {
            'packages': [],
            'leagues': [],
            'availability': {},
            'selected_packages2': [],
            'selected_packages': set()
        })

    # We'll need these for coverage
    game_ids = [g['id'] for g in games]
    tournament_names = {g['tournament_name'] for g in games}

    # -----------------------------------------------------------------
    # 6. Figure out earliest and latest match date
    # -----------------------------------------------------------------
    dates = [g['starts_at'] for g in games]
    earliest_date = min(dates)
    latest_date = max(dates)

    # Function to compute how many months from earliest_date to latest_date inclusive
    def month_diff(d1, d2):
        """
        Return the number of months between d1 and d2, inclusive.
        e.g.: d1 = 2024-05-01, d2 = 2024-08-30 => 4 (May..Aug)
        """
        return ((d2.year - d1.year) * 12 + (d2.month - d1.month)) + 1

    # The number of months we actually need coverage for
    needed_months = month_diff(earliest_date, latest_date)
    if needed_months < 1:
        needed_months = 1  # safety net

    # 7. Fetch streaming_offers and unique packages
    streaming_offers = (
        streaming_offer.objects
        .filter(game_id__in=game_ids)
        .select_related('streaming_package_id', 'game_id')
    )
    unique_package_ids = streaming_offers.values_list('streaming_package_id', flat=True).distinct()

    # 8. Annotate packages with float prices, including annual_only
    packages_qs = (
        streaming_package.objects
        .filter(id__in=unique_package_ids)
        .annotate(
            # monthly in EUR
            monthly_price_cents_float=Case(
                When(monthly_price_cents__isnull=True, then=Value(None)),
                When(monthly_price_cents=0, then=Value(0.0)),
                default=F('monthly_price_cents') / 100.0,
                output_field=FloatField()
            ),
            # yearly in EUR
            monthly_price_yearly_subscription_in_cents_float=Case(
                When(monthly_price_yearly_subscription_in_cents__isnull=True, then=Value(None)),
                When(monthly_price_yearly_subscription_in_cents=0, then=Value(0.0)),
                default=F('monthly_price_yearly_subscription_in_cents') / 100.0,
                output_field=FloatField()
            )
        )
        # Suppose your model has a boolean field `annual_only`
        # If not, you can remove or adapt this.
        # .values(...) to also fetch `annual_only` if you want it in code below
        # For illustration, let's assume you can do:
        # .values(
        #    'id', 'name', 'annual_only',
        #    'monthly_price_cents_float',
        #    'monthly_price_yearly_subscription_in_cents_float', ...
        # )
    )

    # 9. Build package_info
    packages = []
    package_info = {}
    for pak in packages_qs:
        # If using .values(), you might do: is_annual_only = pak['annual_only']
        # or if your streaming_package model has an `annual_only` field:
        # is_annual_only = pak.annual_only
        
        # Example: we call it is_annual_only.
        # If your DB doesn't have it, you'll have to store it in the model.
        is_annual_only = getattr(pak, 'annual_only', False)  # default False if not present

        package_data = {
            'id': pak.id,
            'name': pak.name,
            'logo': 'nologo.png',
            'annual_only': is_annual_only,  # store the boolean
            'monthly_price_eur': getattr(pak, 'monthly_price_cents_float', 0.0),
            'yearly_price_eur': getattr(pak, 'monthly_price_yearly_subscription_in_cents_float', 0.0)
        }
        packages.append(package_data)
        package_info[pak.id] = package_data

    # --------------------------------------------------------------
    # 10. Calculate "cost for needed_months" for each package
    # --------------------------------------------------------------
    def compute_partial_cost(pkg_id):
        pkg = package_info[pkg_id]
        monthly = pkg['monthly_price_eur'] or 0.0
        yearly = pkg['yearly_price_eur'] or 0.0
        annual_only = pkg['annual_only']

        # If the package is strictly annual-only, we must pay yearly no matter what:
        if annual_only:
            # If the yearly is 0 => treat as 0.01 or handle differently
            return yearly if yearly > 0 else 0.01

        # Otherwise, we can compare monthly vs. yearly:
        # if monthly=0 => treat as 0.01
        if monthly <= 0:
            monthly = 0.01
        if yearly <= 0:
            yearly = 0.01

        monthly_cost = monthly * needed_months
        partial_cost = min(monthly_cost, yearly)
        return partial_cost

    # ------------------------------------------------------------
    # 11. Build coverage_by_game => if live or highlights => covers
    # ------------------------------------------------------------
    package_coverage_by_game = defaultdict(set)
    for off in streaming_offers:
        pkg_id = off.streaming_package_id.id
        if off.live or off.highlights:
            package_coverage_by_game[pkg_id].add(off.game_id.id)

    # ------------------------------------------------------------
    # 12. Build availability data (live vs highlight) for the template
    # ------------------------------------------------------------
    tournament_to_game_ids = defaultdict(set)
    for g in games:
        tournament_to_game_ids[g['tournament_name']].add(g['id'])

    package_coverage_live = defaultdict(set)
    package_coverage_highlight = defaultdict(set)
    for off in streaming_offers:
        pkg_id = off.streaming_package_id.id
        g_id = off.game_id.id
        if off.live:
            package_coverage_live[pkg_id].add(g_id)
        if off.highlights:
            package_coverage_highlight[pkg_id].add(g_id)

    availability = {}
    for pkg_id in unique_package_ids:
        availability[pkg_id] = {}
        for t_name, t_game_ids in tournament_to_game_ids.items():
            total_count = len(t_game_ids)
            if total_count == 0:
                availability[pkg_id][t_name] = {
                    'live': False,
                    'live_partial': False,
                    'highlight': False,
                    'highlight_partial': False
                }
                continue

            live_count = len(package_coverage_live[pkg_id] & t_game_ids)
            live_ratio = live_count / total_count
            if live_ratio == 1.0:
                live_val = True
                live_partial = False
            elif live_ratio == 0.0:
                live_val = False
                live_partial = False
            else:
                live_val = False
                live_partial = True

            hi_count = len(package_coverage_highlight[pkg_id] & t_game_ids)
            hi_ratio = hi_count / total_count
            if hi_ratio == 1.0:
                hi_val = True
                hi_partial = False
            elif hi_ratio == 0.0:
                hi_val = False
                hi_partial = False
            else:
                hi_val = False
                hi_partial = True

            availability[pkg_id][t_name] = {
                'live': live_val,
                'live_partial': live_partial,
                'highlight': hi_val,
                'highlight_partial': hi_partial
            }

    # ------------------------------------------------------------
    # 13. "Best combination" using coverage/cost ratio
    #     cost = compute_partial_cost, which handles annual_only
    # ------------------------------------------------------------
    uncovered_game_ids = {g['id'] for g in games}
    selected_packages = set()

    while uncovered_game_ids:
        best_package = None
        best_ratio = 0.0

        for pkg_id in unique_package_ids:
            if pkg_id in selected_packages:
                continue

            newly_covered = len(package_coverage_by_game[pkg_id] & uncovered_game_ids)
            if newly_covered == 0:
                continue

            partial_cost = compute_partial_cost(pkg_id)  # respects annual_only
            ratio = newly_covered / partial_cost if partial_cost else float('inf')

            if ratio > best_ratio:
                best_ratio = ratio
                best_package = pkg_id

        if not best_package:
            # no improvement
            break

        selected_packages.add(best_package) # list of bast package id's 
        uncovered_game_ids -= package_coverage_by_game[best_package]

    # ------------------------------------------------------------
    # 14. If no lieges, show all tournaments
    # ------------------------------------------------------------
    if not selected_lieges_names:
        selected_lieges_names = list(tournament_names)

    # ------------------------------------------------------------
    # 15. Build final selected packages with annotated prices
    # ------------------------------------------------------------
    selected_packages_qs = (
        streaming_package.objects
        .filter(id__in=selected_packages)
        .annotate(
            monthly_price_cents_float=Coalesce(
                NullIf(F('monthly_price_cents'), 0) / 100.0, 
                Value(None)
            ),
            monthly_price_yearly_subscription_in_cents_float=Coalesce(
                NullIf(F('monthly_price_yearly_subscription_in_cents'), 0) / 100.0, 
                Value(None)
            )
        )
    )

    # ------------------------------------------------------------
    # 16. Build final context
    # ------------------------------------------------------------
    context = {
        'packages': packages,
        'leagues': selected_lieges_names,
        'availability': availability,
        'selected_packages': selected_packages_qs,
    }
    cache.set(cache_key, context, timeout=None)

    return render(request, 'result-v3.html', context)

def display_table(request):
    if request.method != "POST":
        return redirect(reverse('homepage'))
    
    # 1. Retrieve selected clubs and lieges from the POST data
    selected_clubs = request.POST.getlist('clubs')
    selected_lieges = request.POST.getlist('lieges')
    
    # 2. Cache logic
    cache_key = generate_cache_key(selected_clubs, selected_lieges)
    context = cache.get(cache_key)
    if context and False:  # For demo, skip the cache
        return render(request, 'result-v3.html', context)

    # 3. Gather league names and clubs
    if selected_lieges:
        selected_lieges_names = list(
            lieges.objects.filter(id__in=selected_lieges)
                          .order_by('-score')
                          .values_list('name', flat=True)
        )
    else:
        selected_lieges_names = []

    if selected_clubs:
        club_qs = clubs.objects.filter(id__in=selected_clubs)
    else:
        club_qs = clubs.objects.all()
    club_names = list(club_qs.values_list('name', flat=True))

    # 4. Build a union (OR) query for games
    games_query = Q()
    
    if club_names:
        club_query = Q(team_home__in=club_names) | Q(team_away__in=club_names)
        games_query |= club_query

    if selected_lieges_names:
        liege_query = Q(tournament_name__in=selected_lieges_names)
        games_query |= liege_query

    # If user selected nothing, fetch all games or none
    if not club_names and not selected_lieges_names:
        games_query = Q()  # means fetch all

    games_qs = game.objects.filter(games_query).values('id', 'tournament_name', 'starts_at')
    games = list(games_qs)
    if not games:
        # No relevant games => return empty context
        return render(request, 'result-v3.html', {
            'packages': [],
            'leagues': [],
            'availability': {},
            'selected_packages2': [],
            'selected_packages': set()
        })

    # We'll need these for coverage
    game_ids = [g['id'] for g in games]
    tournament_names = {g['tournament_name'] for g in games}

    # 5. Determine date range and needed_months
    dates = [g['starts_at'] for g in games]
    earliest_date = min(dates)
    latest_date = max(dates)

    def month_diff(d1, d2):
        """Number of months between d1 and d2, inclusive."""
        return ((d2.year - d1.year) * 12 + (d2.month - d1.month)) + 1

    needed_months = month_diff(earliest_date, latest_date)
    if needed_months < 1:
        needed_months = 1

    # 6. Fetch streaming offers and packages
    streaming_offers = (
        streaming_offer.objects
        .filter(game_id__in=game_ids)
        .select_related('streaming_package_id', 'game_id')
    )
    unique_package_ids = (
        streaming_offers
        .values_list('streaming_package_id', flat=True)
        .distinct()
    )

    packages_qs = (
        streaming_package.objects
        .filter(id__in=unique_package_ids)
        .annotate(
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
    )

    # Build a dictionary of packages (for quick cost lookups, etc.)
    package_info = {}
    for pak in packages_qs:
        package_info[pak.id] = {
            'id': pak.id,
            'name': pak.name,
            'annual_only': getattr(pak, 'annual_only', False),
            'monthly_price_eur': getattr(pak, 'monthly_price_cents_float', 0.0),
            'yearly_price_eur': getattr(pak, 'monthly_price_yearly_subscription_in_cents_float', 0.0),
        }

    def compute_partial_cost(pkg_id):
        """
        Return minimal cost of a package for the needed_months window.
        Respects annual_only. 
        """
        pkg = package_info[pkg_id]
        monthly = pkg['monthly_price_eur'] or 0.0
        yearly = pkg['yearly_price_eur'] or 0.0
        if pkg['annual_only']:
            return yearly if yearly > 0 else 0.01
        # Otherwise pick cheaper of paying monthly vs. the yearly subscription
        monthly_cost = (monthly if monthly > 0 else 0.01) * needed_months
        yearly_cost = yearly if yearly > 0 else 0.01
        return min(monthly_cost, yearly_cost)

    # 7. Coverage logic:
    #
    #    Instead of simply “covered if live OR highlight,” 
    #    we’ll define a small numeric coverage:
    #       - 1.0 point if live
    #       - 0.5 point if only highlights
    #
    #    For each package and each game, store how much coverage 
    #    the package can provide.
    #
    #    Then we’ll do a “greedy fractional coverage” approach: 
    #    each game starts with coverage_need=1.0. 
    #    If the package has live => it covers 1.0, 
    #    if only highlights => it covers 0.5 
    #    (or partial if the game still needs some fraction).
    #
    #    For simplicity, if the package has both live & highlights, 
    #    treat it as live=1.0 (full coverage).
    #
    from collections import defaultdict

    coverage_of_game = defaultdict(dict)
    for off in streaming_offers:
        pkg_id = off.streaming_package_id.id
        g_id = off.game_id.id

        # We treat "live" coverage as 1.0, else if only highlight => 0.5
        # If a single offer is live=True and highlight=True, that’s still 1.0 coverage
        # If an offer is just highlight=True, coverage is 0.5
        # If multiple lines exist for same pkg-game, we’ll keep the max coverage
        coverage_points = 0.0
        if off.live:
            coverage_points = 1.0
        elif off.highlights:
            coverage_points = 0.5

        # If multiple streaming_offers rows exist for the same package/game
        # we take the max coverage
        coverage_of_game[pkg_id][g_id] = max(
            coverage_of_game[pkg_id].get(g_id, 0.0), 
            coverage_points
        )

    # Build a list/dict to track how much coverage each game STILL needs
    coverage_need = {}
    for g in games:
        coverage_need[g['id']] = 1.0  # each game wants full coverage (value=1.0)

    selected_packages = set()
    # Because we’re doing a greedy approach, we keep iterating until 
    # coverage_need for all games is ~0 or we can’t improve coverage
    while True:
        best_pkg = None
        best_ratio = 0.0
        best_coverage_gain = 0.0

        for pkg_id in unique_package_ids:
            if pkg_id in selected_packages:
                continue

            # How much coverage can this package still provide 
            # for the uncovered portion of each game?
            # E.g. if a game needs 1.0 coverage, but the package can only do 0.5, 
            # that is 0.5 coverage gained for that game.
            incremental_coverage = 0.0
            for g_id, need_left in coverage_need.items():
                if need_left > 0:  # game not fully covered
                    # coverage potential from this package for that game
                    pkg_covers = coverage_of_game[pkg_id].get(g_id, 0.0)
                    # We can only use min(pkg_covers, need_left)
                    # e.g. if need_left=1.0 but pkg_covers=0.5 => 0.5 coverage gained
                    # or if we still need 0.5 but pkg can do 1 => 0.5 coverage used
                    coverage_gain_for_game = min(pkg_covers, need_left)
                    incremental_coverage += coverage_gain_for_game

            if incremental_coverage > 0:
                cost = compute_partial_cost(pkg_id)
                ratio = incremental_coverage / cost if cost else float('inf')
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_pkg = pkg_id
                    best_coverage_gain = incremental_coverage

        if not best_pkg:
            # No package improves coverage further => break
            break

        # Select that package
        selected_packages.add(best_pkg)
        # Reduce coverage_need for each game
        for g_id, need_left in coverage_need.items():
            if need_left > 0:
                pkg_covers = coverage_of_game[best_pkg].get(g_id, 0.0)
                coverage_need[g_id] = max(0.0, need_left - pkg_covers)

        # If all coverage_need is 0 => done
        if all(needed <= 0 for needed in coverage_need.values()):
            break

    # Build final QS for the selected packages
    selected_packages_qs = (
        streaming_package.objects
        .filter(id__in=selected_packages)
        .annotate(
            monthly_price_cents_float=Coalesce(
                NullIf(F('monthly_price_cents'), 0) / 100.0, 
                Value(None)
            ),
            monthly_price_yearly_subscription_in_cents_float=Coalesce(
                NullIf(F('monthly_price_yearly_subscription_in_cents'), 0) / 100.0, 
                Value(None)
            )
        )
    )

    # Build the availability dictionary exactly as you did before,
    # or adapt it to account for partial coverage. For brevity,
    # we’ll reuse your code for availability:
    tournament_to_game_ids = defaultdict(set)
    for g in games:
        tournament_to_game_ids[g['tournament_name']].add(g['id'])

    package_coverage_live = defaultdict(set)
    package_coverage_highlight = defaultdict(set)
    for off in streaming_offers:
        p_id = off.streaming_package_id.id
        gid = off.game_id.id
        if off.live:
            package_coverage_live[p_id].add(gid)
        if off.highlights:
            package_coverage_highlight[p_id].add(gid)

    availability = {}
    for pkg_id in unique_package_ids:
        availability[pkg_id] = {}
        for t_name, t_game_ids in tournament_to_game_ids.items():
            total_count = len(t_game_ids)
            if total_count == 0:
                availability[pkg_id][t_name] = {
                    'live': False,
                    'live_partial': False,
                    'highlight': False,
                    'highlight_partial': False
                }
                continue

            live_count = len(package_coverage_live[pkg_id] & t_game_ids)
            live_ratio = live_count / total_count
            if live_ratio == 1.0:
                live_val = True
                live_partial = False
            elif live_ratio == 0.0:
                live_val = False
                live_partial = False
            else:
                live_val = False
                live_partial = True

            hi_count = len(package_coverage_highlight[pkg_id] & t_game_ids)
            hi_ratio = hi_count / total_count
            if hi_ratio == 1.0:
                hi_val = True
                hi_partial = False
            elif hi_ratio == 0.0:
                hi_val = False
                hi_partial = False
            else:
                hi_val = False
                hi_partial = True

            availability[pkg_id][t_name] = {
                'live': live_val,
                'live_partial': live_partial,
                'highlight': hi_val,
                'highlight_partial': hi_partial
            }

    # If no lieges selected, show all tournaments
    if not selected_lieges_names:
        selected_lieges_names = list(tournament_names)

    # Build final context
    context = {
        'packages': list(packages_qs),  # or a serialized version
        'leagues': selected_lieges_names,
        'availability': availability,
        'selected_packages': selected_packages_qs,
    }
    cache.set(cache_key, context, timeout=None)

    return render(request, 'result-v3.html', context)
