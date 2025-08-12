from datetime import date, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# DRF (falls du die API nutzt)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import FoodItem, BanditBucket
from .serializers import FoodItemSerializer
from .forms import FoodItemForm
from .rl import bin_days, choose_action
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
# RL-Helfer
# -------------------------
def advice_for_item(user, item):
    """Ermittelt Badge (Sicherheit/Unsicherheit) und merkt die gewählte Aktion für Rewards."""
    days = (item.expiration_date - date.today()).days
    days_bucket = bin_days(days)
    bucket, _ = BanditBucket.objects.get_or_create(
        user=user, days_bin=days_bucket, category=''  # falls du Kategorien hast, hier einsetzen
    )
    action = choose_action(bucket)  # 'warn' oder 'no_warn'
    badge = "Unsicherheit" if action == 'warn' else "Sicherheit"
    return badge, action


def update_reward(user, item, chosen_action):
    """
    Feedback: War die gewählte Aktion korrekt?
    - 'warn' ist korrekt, wenn LM ablief
    - 'no_warn' ist korrekt, wenn LM NICHT ablief
    """
    days_bucket = bin_days((item.expiration_date - item.added_on.date()).days)
    bucket = BanditBucket.objects.get(user=user, days_bin=days_bucket, category='')

    expired = (timezone.now().date() >= item.expiration_date)
    correct = (chosen_action == 'warn' and expired) or (chosen_action == 'no_warn' and not expired)

    if chosen_action == 'warn':
        if correct:
            bucket.warn_alpha += 1
        else:
            bucket.warn_beta += 1
    else:
        if correct:
            bucket.nowarn_alpha += 1
        else:
            bucket.nowarn_beta += 1
    bucket.save()


# -------------------------
# Views
# -------------------------
@login_required
def overview(request):
    """Liste nach MHD-Kategorien, inkl. RL-Badge und Session-Merken der Aktion je Item."""
    all_items = FoodItem.objects.filter(user=request.user).order_by('expiration_date')

    mhd_gt_7 = []
    mhd_lt_7 = []
    expired_0_3 = []
    expired_gt_3 = []

    today = date.today()

    for item in all_items:
        # RL-Badge + Aktion bestimmen
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
    chosen_action = request.session.pop(f"choice_{item.id}", None)
    if chosen_action:
        update_reward(request.user, item, chosen_action)
    item.delete()
    return redirect('overview')


@require_POST
@login_required
def food_change_qty(request, pk, delta):
    item = get_object_or_404(FoodItem, pk=pk, user=request.user)
    try:
        delta = int(delta)
    except ValueError:
        return redirect('overview')

    new_qty = (item.quantity or 0) + delta
    if new_qty <= 0:
        # als "verbraucht" interpretieren -> Reward aktualisieren
        chosen_action = request.session.pop(f"choice_{item.id}", None)
        if chosen_action:
            update_reward(request.user, item, chosen_action)
        item.delete()
    else:
        item.quantity = new_qty
        item.save()
    return redirect('overview')
