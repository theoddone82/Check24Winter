from django.contrib import admin
from csvFileParser.models import game, streaming_package, streaming_offer
from import_export.admin import ImportExportModelAdmin
from .resources import GameResource, StreamingPackageResource, StreamingOfferResource

class GameAdmin(ImportExportModelAdmin):
    ressource_class = GameResource

class StreamingPackageAdmin(ImportExportModelAdmin):
    ressource_class = StreamingPackageResource

class StreamingOfferAdmin(ImportExportModelAdmin):
    ressource_class = StreamingOfferResource

admin.site.register(game, GameAdmin)
admin.site.register(streaming_package, StreamingPackageAdmin)
admin.site.register(streaming_offer, StreamingOfferAdmin)