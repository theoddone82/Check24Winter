from django.db import models

# Create your models here.
class game(models.Model):
    team_home = models.CharField(max_length=100)
    team_away = models.CharField(max_length=100)
    starts_at = models.DateTimeField()
    tournament_name = models.CharField(max_length=100)

class streaming_package(models.Model):
    name = models.CharField(max_length=100)
    monthly_price_cents = models.IntegerField(null=True)
    monthly_price_yearly_subscription_cents = models.IntegerField(null=True)


class streaming_offer(models.Model):
    game_id = models.ForeignKey(game, on_delete=models.CASCADE)
    streaming_package_id = models.ForeignKey(streaming_package, on_delete=models.CASCADE)
    live    = models.BooleanField()
    highlights = models.BooleanField()
