from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets
from .models import FoodItem
from .serializers import FoodItemSerializer
from .forms import FoodItemForm

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

# API bleibt
class FoodItemViewSet(viewsets.ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer

@login_required
def overview(request):
    today = date.today()
    in_7 = today + timedelta(days=7)
    three_days_ago = today - timedelta(days=3)

    # Kategorien bauen
    mhd_gt_7      = FoodItem.objects.filter(expiration_date__gt=in_7).order_by('expiration_date')
    mhd_lt_7      = FoodItem.objects.filter(expiration_date__gt=today, expiration_date__lte=in_7).order_by('expiration_date')
    expired_0_3   = FoodItem.objects.filter(expiration_date__gt=three_days_ago, expiration_date__lte=today).order_by('expiration_date')
    expired_gt_3  = FoodItem.objects.filter(expiration_date__lte=three_days_ago).order_by('expiration_date')

    ctx = {
        'mhd_gt_7': mhd_gt_7,
        'mhd_lt_7': mhd_lt_7,
        'expired_0_3': expired_0_3,
        'expired_gt_3': expired_gt_3,
    }
    return render(request, 'vorrat/overview.html', ctx)

@login_required
def food_add(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('overview')
    else:
        form = FoodItemForm()
    return render(request, 'vorrat/food_form.html', {'form': form})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # optional: direkt einloggen, sonst auf login umleiten
            # auth_login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})