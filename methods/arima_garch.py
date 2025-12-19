import pandas as pd
import numpy as np
import warnings

try:
    from arch import arch_model

    HAS_ARCH = True
except ImportError:
    HAS_ARCH = False


def forecast_arima_garch(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Strategia 'ARIMA-GARCH'.
    Dynamicznie obsługuje interwał (1h, 1d) przekazany w danych.
    """
    clean_series = series.dropna()

    # --- FIX: Dynamiczne wykrywanie częstotliwości ---
    try:
        if clean_series.index.freq is None:
            inferred_freq = pd.infer_freq(clean_series.index)
            if inferred_freq:
                clean_series = clean_series.asfreq(inferred_freq, method='ffill')
    except Exception:
        pass
    # -----------------------------------------------

    last_price = clean_series.iloc[-1]

    if len(clean_series) < 50:
        return pd.Series([last_price] * horizon)

    # Obliczanie zwrotów (skalowane x100 dla stabilności GARCH)
    returns = 100 * clean_series.pct_change().dropna()

    if not HAS_ARCH:
        print("Brak biblioteki 'arch'. Zainstaluj: pip install arch")
        return pd.Series([last_price] * horizon)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # GARCH(1,1)
            model = arch_model(returns, vol='Garch', p=1, q=1, mean='Constant', dist='Normal')
            # rescale=False zapobiega automatycznemu przeskalowaniu, jeśli dane są już x100
            res = model.fit(disp='off', options={'maxiter': 200})

            # Prognoza wariancji/średniej
            forecasts = res.forecast(horizon=horizon)

            # Pobieramy prognozowaną średnią (mean) zwrotu
            forecast_returns = forecasts.mean.iloc[-1].values

        # Rekonstrukcja ceny
        forecast_prices = []
        current_price = last_price

        for ret in forecast_returns:
            # ret jest w %, więc dzielimy przez 100
            next_price = current_price * (1 + ret / 100)
            forecast_prices.append(next_price)
            current_price = next_price

        return pd.Series(data=forecast_prices)

    except Exception as e:
        print(f"Błąd ARIMA-GARCH: {e}")
        return pd.Series([last_price] * horizon)


def get_forecast_method():
    return {
        "key": "arima_garch",
        "name": "ARIMA-GARCH (Auto-Freq)",
        "category": "Statistical Models",
        "forecast": forecast_arima_garch,
        "description": "Model hybrydowy uwzględniający zmienność (GARCH). Obsługuje dynamiczne interwały.",
        "color": "#00ced1"
    }