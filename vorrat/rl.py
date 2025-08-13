from __future__ import annotations

def normalize_name(name: str) -> str:
    """Einheitliche Normalisierung, damit 'Apfel', 'apfel ' etc. zusammenlaufen."""
    return (name or "").strip().lower()

def choose_action_for_stat(success: int, failure: int) -> str:
    """
    Deterministische Entscheidung pro Name:
    - Cold start (0/0) => 'no_warn' (Sicherheit).
    - Sonst: Beta-Mittelwert vergleichen.
    """
    if success == 0 and failure == 0:
        return 'no_warn'  # Sicherheit

    p_success = (1 + success) / (1 + success + 1 + failure)
    return 'no_warn' if p_success >= 0.5 else 'warn'

