# your_app/resources.py

from import_export import resources
from csvFileParser.models import game, streaming_package, streaming_offer

class GameResource(resources.ModelResource):
    class Meta:
        model = game

class StreamingPackageResource(resources.ModelResource):
    class Meta:
        model = streaming_package

class StreamingOfferResource(resources.ModelResource):
    class Meta:
        model = streaming_offer

