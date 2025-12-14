import pandas as pd
import numpy as np


def forecast_mamba(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Strategia 'CryptoMamba' - Momentum Trend Follower.
    Opiera się na dynamice (Gap) między szybką (EMA 9) a wolną (EMA 21) średnią.
    Projektuje przyszłość zakładając kontynuację pędu z lekkim wygaszaniem (Decay).
    """
    # 1. Czyszczenie danych
    clean_series = series.dropna()

    # Potrzebujemy minimum 21 punktów do obliczenia wskaźników
    if len(clean_series) < 21:
        # Fallback: jeśli za mało danych, zwróć ostatnią cenę (płaska linia)
        return pd.Series([clean_series.iloc[-1]] * horizon)

    # 2. Obliczanie wskaźników (Szybka i Wolna EMA)
    # EMA reaguje szybciej na zmiany cen niż zwykła średnia (SMA)
    ema_fast = clean_series.ewm(span=9, adjust=False).mean()
    ema_slow = clean_series.ewm(span=21, adjust=False).mean()

    # 3. Analiza Momentum ("Paszcza Mamby")
    last_price = clean_series.iloc[-1]
    last_fast = ema_fast.iloc[-1]
    last_slow = ema_slow.iloc[-1]

    # Obliczamy różnicę (Momentum)
    momentum_gap = last_fast - last_slow

    # Normalizujemy siłę trendu (żeby nie wystrzeliła w kosmos)
    # Zakładamy, że pęd ciągnie cenę, ale z każdym dniem traci 5% siły (opór rynku)
    decay_factor = 0.95

    forecast_values = []
    current_price = last_price

    # 4. Generowanie prognozy
    for _ in range(horizon):
        # Mamba logic: Cena przesuwa się w kierunku momentum
        # Dodajemy ułamek momentum do ceny
        step_move = momentum_gap * 0.5

        current_price += step_move
        forecast_values.append(current_price)

        # Z każdym krokiem momentum słabnie (rynek dąży do równowagi)
        momentum_gap *= decay_factor

    return pd.Series(data=forecast_values)


def get_forecast_method():
    return {
        "key": "crypto_mamba",
        "name": "Crypto Mamba (Momentum)",
        "category": "Advanced Strategies",
        "forecast": forecast_mamba,
        "description": "Agresywna strategia oparta na przecięciach EMA 9/21. Wykrywa pęd rynku.",
        "color": "#00ff00"  # Jadowita zieleń (Lime Green)
    }