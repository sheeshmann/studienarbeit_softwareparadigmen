from django.contrib import admin
from .models import FoodItem, ItemStat  # ggf. weitere Modelle importieren

admin.site.register(FoodItem)
admin.site.register(ItemStat)