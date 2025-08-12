from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets
from .models import FoodItem
from .serializers import FoodItemSerializer
from .forms import FoodItemForm

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

from rest_framework.permissions import IsAuthenticated

from django.views.decorators.http import require_POST

# API bleibt
class FoodItemViewSet(viewsets.ModelViewSet):
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]  # API nur für eingeloggte Nutzer

    queryset = FoodItem.objects.none()  # <- neu

    def get_queryset(self):
        return FoodItem.objects.filter(user=self.request.user).order_by('expiration_date')

@login_required
def overview(request):
    today = date.today()
    in_7 = today + timedelta(days=7)
    three_days_ago = today - timedelta(days=3)

    qs = FoodItem.objects.filter(user=request.user)
    mhd_gt_7     = qs.filter(expiration_date__gt=in_7).order_by('expiration_date')
    mhd_lt_7     = qs.filter(expiration_date__gt=today, expiration_date__lte=in_7).order_by('expiration_date')
    expired_0_3  = qs.filter(expiration_date__gt=three_days_ago, expiration_date__lte=today).order_by('expiration_date')
    expired_gt_3 = qs.filter(expiration_date__lte=three_days_ago).order_by('expiration_date')

    return render(request, 'vorrat/overview.html', {
        'mhd_gt_7': mhd_gt_7,
        'mhd_lt_7': mhd_lt_7,
        'expired_0_3': expired_0_3,
        'expired_gt_3': expired_gt_3,
    })

@login_required
def food_add(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user        # <- Besitzer setzen
            item.save()
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

@require_POST
@login_required
def food_delete(request, pk):
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    item.delete()
    return redirect('overview')

@require_POST
@login_required
def food_change_qty(request, pk, delta):
    """delta ist z.B. -1 oder +1"""
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    try:
        delta = int(delta)
    except ValueError:
        return redirect('overview')

    new_qty = (item.quantity or 0) + delta
    if new_qty <= 0:
        item.delete()          # bei 0 oder weniger: Eintrag entfernen
    else:
        item.quantity = new_qty
        item.save()
    return redirect('overview')