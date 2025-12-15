import pandas as pd
import numpy as np


def forecast_monte_carlo(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Strategia 'Monte Carlo Drift'.
    Modeluje geometryczne ruchy Browna (GBM). Oblicza średni dzienny zwrot (log returns)
    i historyczną zmienność (variance), aby wyznaczyć najbardziej prawdopodobną ścieżkę.
    """
    # 1. Obliczanie logarytmicznych zwrotów (lepsze dla krypto niż procentowe)
    clean_series = series.dropna()
    if len(clean_series) < 30:
        return pd.Series([clean_series.iloc[-1]] * horizon)

    log_returns = np.log(clean_series / clean_series.shift(1)).dropna()

    # 2. Parametry statystyczne
    mu = log_returns.mean()  # Średni zwrot (Drift)
    var = log_returns.var()  # Wariancja (Zmienność^2)
    last_price = clean_series.iloc[-1]

    # Drift deterministyczny (dla pojedynczej linii prognozy)
    # Wzór: drift = mu - (0.5 * var)
    drift = mu - (0.5 * var)

    # Odchylenie standardowe (zmienność)
    sigma = log_returns.std()

    forecast_values = []
    current_price = last_price

    # 3. Projekcja
    # Uwaga: W pełnym Monte Carlo dodalibyśmy element losowy (stochastyczny).
    # Tutaj, aby wykres był stabilny dla użytkownika, projektujemy "Expected Value".

    for _ in range(horizon):
        # Stosujemy sam dryf bez szumu losowego dla czytelności wykresu
        # Cena(t) = Cena(t-1) * e^(drift)
        next_price = current_price * np.exp(drift)
        forecast_values.append(next_price)
        current_price = next_price

    return pd.Series(data=forecast_values)


def get_forecast_method():
    return {
        "key": "monte_carlo",
        "name": "Monte Carlo (Expected Path)",
        "category": "Statistical Models",
        "forecast": forecast_monte_carlo,
        "description": "Model stochastyczny oparty na Geometrycznych Ruchach Browna (GBM). Wyznacza statystyczny dryf ceny.",
        "color": "#ff00ff"  # Magenta
    }