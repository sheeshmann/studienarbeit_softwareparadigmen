from django.urls import path
from .views import food_list, food_add

urlpatterns = [
    path('', food_list, name='food-list'),
    path('add/', food_add, name='food-add'), 
]