from datetime import date
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# DRF (optional)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import FoodItem, ItemStat
from .serializers import FoodItemSerializer
from .forms import FoodItemForm
from .rl import normalize_name, choose_action_for_stat
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login


# -------------------------
# API (optional)
# -------------------------
class FoodItemViewSet(viewsets.ModelViewSet):
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = FoodItem.objects.none()

    def get_queryset(self):
        return FoodItem.objects.filter(user=self.request.user).order_by('expiration_date')


# -------------------------
# RL-Helfer (pro Name & User)
# -------------------------
def advice_for_item(user, item):
    """
    Liefert ('Sicherheit'/'Unsicherheit') und die intern gewählte Aktion ('no_warn'/'warn')
    auf Basis der pro-Name-Statistik für diesen User.
    """
    norm_name = normalize_name(item.name)
    stat, _ = ItemStat.objects.get_or_create(user=user, name=norm_name)
    action = choose_action_for_stat(stat.success, stat.failure)  # 'no_warn' oder 'warn'
    badge = "Sicherheit" if action == 'no_warn' else "Unsicherheit"
    return badge, action


def update_reward(user, item, chosen_action):
    """
    Feedback beim Verbrauch/Löschen:
    - abgelaufen -> failure++
    - NICHT abgelaufen -> success++
    """
    norm_name = normalize_name(item.name)
    stat, _ = ItemStat.objects.get_or_create(user=user, name=norm_name)

    expired = (timezone.now().date() >= item.expiration_date)
    if expired:
        stat.failure += 1
    else:
        stat.success += 1
    stat.save()



# -------------------------
# Views
# -------------------------
@login_required
def overview(request):
    """Liste nach MHD-Kategorien, inkl. pro-Name Badge und Session-Merken der Aktion je Item."""
    all_items = FoodItem.objects.filter(user=request.user).order_by('expiration_date')

    mhd_gt_7, mhd_lt_7, expired_0_3, expired_gt_3 = [], [], [], []
    today = date.today()

    for item in all_items:
        # RL-Badge + Aktion bestimmen (pro Name & User)
        badge, action = advice_for_item(request.user, item)
        item.badge = badge
        # Aktion für Reward-Update merken
        request.session[f"choice_{item.id}"] = action

        days_to_expiry = (item.expiration_date - today).days
        if days_to_expiry > 7:
            mhd_gt_7.append(item)
        elif 0 < days_to_expiry <= 7:
            mhd_lt_7.append(item)
        elif -3 <= days_to_expiry <= 0:
            expired_0_3.append(item)
        else:
            expired_gt_3.append(item)

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
            item.user = request.user
            item.save()

            # Cold-start sicherstellen (Stat existiert):
            ItemStat.objects.get_or_create(
                user=request.user,
                name=normalize_name(item.name),
            )
            return redirect('overview')
    else:
        form = FoodItemForm()
    return render(request, 'vorrat/food_form.html', {'form': form})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # optional: direkt einloggen
            # auth_login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@require_POST
@login_required
def food_delete(request, pk):
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    # Die angezeigte Aktion war nur UI; Reward hängt vom Outcome ab:
    _ = request.session.pop(f"choice_{item.id}", None)
    update_reward(request.user, item, _)
    item.delete()
    return redirect('overview')


@require_POST
@login_required
def food_change_qty(request, pk, delta):
    """delta ist z.B. -1 oder +1. Wenn Menge <= 0 -> als 'verbraucht' werten."""
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    try:
        delta = int(delta)
    except ValueError:
        return redirect('overview')

    new_qty = (item.quantity or 0) + delta
    if new_qty <= 0:
        _ = request.session.pop(f"choice_{item.id}", None)
        update_reward(request.user, item, _)
        item.delete()
    else:
        item.quantity = new_qty
        item.save()
    return redirect('overview')
