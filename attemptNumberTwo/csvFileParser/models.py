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
    monthly_price_yearly_subscription_in_cents = models.IntegerField(null=True)


class streaming_offer(models.Model):
    game_id = models.ForeignKey(game, on_delete=models.CASCADE)
    streaming_package_id = models.ForeignKey(streaming_package, on_delete=models.CASCADE)
    live    = models.BooleanField()
    highlights = models.BooleanField()

class clubs(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField(null=True)

    def __str__(self):
        return self.name  # This will be displayed in the ModelChoiceField
    
class lieges(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField(null=True)
    def __str__(self):
        return self.name  # This will be displayed in the ModelChoiceField
    
class db_cache(models.Model):
    key = models.CharField(max_length=10000)
    value = models.CharField(max_length=10000)
    def __str__(self):
        return self.key  # This will be displayed in the ModelChoiceField
    
class BestStreamingProvider(models.Model):
    club = models.ForeignKey(clubs, on_delete=models.CASCADE)
    streaming_package = models.ForeignKey(streaming_package, on_delete=models.CASCADE)
    is_best_provider = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.club.name} - {self.streaming_package.name}"
