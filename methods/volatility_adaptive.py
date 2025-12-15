import pandas as pd
import numpy as np

def forecast_volatility_adaptive(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Strategia 'Volatility Adaptive'.
    Wykorzystuje hipotezę klastrowania zmienności.
    Dostosowuje prognozę w oparciu o to, jak "szeroki" jest rynek (ATR proxy).
    """
    clean_series = series.dropna()
    if len(clean_series) < 15:
        return pd.Series([clean_series.iloc[-1]] * horizon)

    # 1. Obliczanie uproszczonego ATR (zmienność na podstawie High-Low proxy z Close)
    # Używamy odchylenia standardowego z ostatnich 14 okresów jako miary zmienności
    window = 14
    rolling_std = clean_series.rolling(window=window).std()
    current_volatility = rolling_std.iloc[-1]

    # Średnia zmienność z przeszłości (baza)
    avg_volatility = rolling_std.mean()

    # 2. Określenie kierunku (Regresja liniowa na ostatnich 7 świecach)
    y = clean_series.iloc[-7:].values
    x = np.arange(len(y))

    # Slope (nachylenie) linii a
    slope, _ = np.polyfit(x, y, 1)

    # 3. Współczynnik agresji
    # Jeśli obecna zmienność > średnia, rynek jest w fazie wybicia -> zwiększamy mnożnik
    volatility_ratio = current_volatility / avg_volatility if avg_volatility > 0 else 1.0

    # Ograniczamy ratio, żeby nie "eksplodowało" przy pompach
    volatility_ratio = min(volatility_ratio, 2.0)

    last_price = clean_series.iloc[-1]
    forecast_values = []
    current_price = last_price

    for _ in range(horizon):
        # Prognozowany ruch = nachylenie * mnożnik zmienności
        step = slope * volatility_ratio

        current_price += step
        forecast_values.append(current_price)

        # Z każdym krokiem zmienność "wraca do średniej" (mean reversion)
        # więc zmniejszamy wpływ volatility_ratio w stronę 1.0
        volatility_ratio = (volatility_ratio + 1.0) / 2

    return pd.Series(data=forecast_values)

def get_forecast_method():
    return {
        "key": "volatility_adaptive",
        "name": "Volatility Adaptive",
        "category": "Advanced Strategies",
        "forecast": forecast_volatility_adaptive,
        "description": "Dostosowuje siłę trendu do bieżącej zmienności rynku (Volatility Clustering).",
        "color": "#00d4ff"  # Cyjan
    }