from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import FoodItem
from .serializers import FoodItemSerializer
from .forms import FoodItemForm 

class FoodItemViewSet(viewsets.ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer

def food_list(request):
    foods = FoodItem.objects.all()
    return render(request, 'vorrat/food_list.html', {'foods': foods})

def food_add(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('food-list')
    else:
        form = FoodItemForm()
    return render(request, 'vorrat/food_form.html', {'form': form})