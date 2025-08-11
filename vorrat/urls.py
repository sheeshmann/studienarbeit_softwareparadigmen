from django.urls import path
from .views import overview, food_add, signup

urlpatterns = [
    path('', overview, name='overview'),
    path('add/', food_add, name='food-add'), 
    path('accounts/signup/', signup, name='signup'),
]