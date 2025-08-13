from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_items', null=True, blank=True)  # neu
    name = models.CharField(max_length=100)
    quantity = models.FloatField(verbose_name="Anzahl")
    expiration_date = models.DateField(verbose_name="Ablaufdatum")
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class BanditBucket(models.Model):
    # Beispiel-Bucket: days_to_expiry_bin + optional category + user-specific
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # personalisiert? sonst None
    days_bin = models.CharField(max_length=20)    # e.g. "0-2", "3-6", "7-14", ">14"
    category = models.CharField(max_length=50, blank=True)  # falls du Kategorien hast

    # Beta-Parameter für jede Aktion
    warn_alpha  = models.FloatField(default=1.0)
    warn_beta   = models.FloatField(default=1.0)
    nowarn_alpha = models.FloatField(default=1.0)
    nowarn_beta  = models.FloatField(default=1.0)

    class Meta:
        unique_together = ('user', 'days_bin', 'category')


class ItemStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # exakt der im Formular eingegebene Name; wir normalisieren zusätzlich in Code
    name = models.CharField(max_length=120)

    # Beta(1,1) Prior -> wir speichern Zähler
    success = models.PositiveIntegerField(default=0)  # verbraucht vor MHD
    failure = models.PositiveIntegerField(default=0)  # abgelaufen

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.username}:{self.name} (S={self.success}/F={self.failure})"
