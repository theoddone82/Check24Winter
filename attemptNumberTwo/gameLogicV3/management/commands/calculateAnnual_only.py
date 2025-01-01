from django.core.management.base import BaseCommand
from csvFileParser.models import game, streaming_package
from django.db.models import Q

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # go through all streaming_package and if a monthly price is Null set the annual_only to True
        packages = streaming_package.objects.all()
        for pak in packages:
            if pak.monthly_price_cents is None:
                pak.annual_only = True
                pak.save()
            else:
                pak.annual_only = False
                pak.save()
