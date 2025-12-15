import pandas as pd
import numpy as np


def forecast_holt(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Strategia 'Holt's Linear Trend'.
    Zaawansowana metoda wygładzania wykładniczego, która uczy się dwóch parametrów:
    1. Level (L) - aktualny poziom ceny
    2. Trend (B) - tempo zmian (slope)
    """
    clean_series = series.dropna()
    values = clean_series.values
    n = len(values)

    if n < 10:
        return pd.Series([values[-1]] * horizon)

    # Parametry optymalizowane (alfa dla poziomu, beta dla trendu)
    # Dla krypto przyjmujemy dość reaktywne wartości
    alpha = 0.6  # Waga dla obecnej ceny
    beta = 0.3  # Waga dla zmiany trendu

    # Inicjalizacja
    level = values[0]
    trend = values[1] - values[0]

    # Uczenie modelu na danych historycznych
    for i in range(1, n):
        last_level = level
        current_val = values[i]

        # Aktualizacja poziomu
        level = alpha * current_val + (1 - alpha) * (last_level + trend)
        # Aktualizacja trendu
        trend = beta * (level - last_level) + (1 - beta) * trend

    # Prognozowanie
    forecast_values = []

    # Tłumienie trendu (Damping) - ważne w krypto, bo trendy rzadko idą w nieskończoność prosto
    damping_factor = 0.98

    for h in range(1, horizon + 1):
        # Forecast = Level + (h * Trend)
        # Z zastosowaniem tłumienia:
        current_trend = trend * (damping_factor ** h)
        pred = level + (h * current_trend)
        forecast_values.append(pred)

    return pd.Series(data=forecast_values)


def get_forecast_method():
    return {
        "key": "holt_linear",
        "name": "Holt's Linear Trend",
        "category": "Econometrics",
        "forecast": forecast_holt,
        "description": "Podwójne wygładzanie wykładnicze. Oddziela poziom ceny od siły trendu.",
        "color": "#ffaa00"  # Orange
    }