# vorrat/rl.py
from __future__ import annotations
import random
from typing import TYPE_CHECKING

# Optional: nur für den Editor-Typcheck, nicht zur Laufzeit importieren (vermeidet Zyklen)
if TYPE_CHECKING:
    from .models import BanditBucket  # nur für Type Hints, kein Runtime-Import

def bin_days(days: int) -> str:
    if days <= 2:
        return "0-2"
    if days <= 6:
        return "3-6"
    if days <= 14:
        return "7-14"
    return ">14"

def sample_beta(a: float, b: float) -> float:
    # Beta-Sample via Gamma-Samples
    x = random.gammavariate(a, 1.0)
    y = random.gammavariate(b, 1.0)
    return x / (x + y)

def choose_action(bucket: BanditBucket):
    # Falls der Bucket noch keine Erfahrungswerte hat → Standard "no_warn" (Sicherheit)
    if (bucket.warn_alpha, bucket.warn_beta, bucket.nowarn_alpha, bucket.nowarn_beta) == (1, 1, 1, 1):
        return 'no_warn'

    theta_warn = sample_beta(bucket.warn_alpha, bucket.warn_beta)
    theta_nowarn = sample_beta(bucket.nowarn_alpha, bucket.nowarn_beta)
    return 'warn' if theta_warn >= theta_nowarn else 'no_warn'
