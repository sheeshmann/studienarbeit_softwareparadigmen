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
    chosen_action = request.session.get(f"choice_{item.id}")
    if chosen_action:
        update_reward(request.user, item, chosen_action)
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


from .rl import bin_days, choose_action
from .models import BanditBucket
from datetime import date

def advice_for_item(user, item):
    days = (item.expiration_date - date.today()).days
    days_bucket = bin_days(days)
    bucket, _ = BanditBucket.objects.get_or_create(
        user=user, days_bin=days_bucket, category=''  # oder item.category falls vorhanden
    )
    action = choose_action(bucket)
    badge = "Unsicherheit" if action == 'warn' else "Sicherheit"
    return badge, bucket, action

from django.utils import timezone

def update_reward(user, item, chosen_action):
    from .models import BanditBucket
    from .rl import bin_days
    days_bucket = bin_days((item.expiration_date - item.added_on.date()).days)  # oder days_to_expiry zum Entscheidzeitpunkt, wenn gespeichert
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


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from .models import FoodItem
from .rl import advice_for_item  # deine RL-Funktion importieren

@login_required
def overview(request):
    # Items des eingeloggten Nutzers holen
    all_items = FoodItem.objects.filter(user=request.user).order_by('expiration_date')

    # Kategorien nach MHD
    mhd_gt_7 = []
    mhd_lt_7 = []
    expired_0_3 = []
    expired_gt_3 = []

    for item in all_items:
        # RL Badge setzen
        badge, _, _ = advice_for_item(request.user, item)
        item.badge = badge  # Attribut für Template

        days_to_expiry = (item.expiration_date - date.today()).days
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

