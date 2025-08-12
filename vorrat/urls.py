from django.urls import path
from .views import overview, food_add, signup, food_delete, food_change_qty

urlpatterns = [
    path('', overview, name='overview'),
    path('add/', food_add, name='food-add'),
    path('item/<int:pk>/delete/', food_delete, name='food-delete'),
    path('item/<int:pk>/change/<int:delta>/', food_change_qty, name='food-change-qty'),
    path('accounts/signup/', signup, name='signup'),
]
