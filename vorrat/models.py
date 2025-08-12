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