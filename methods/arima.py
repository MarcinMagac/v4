import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA as StatsARIMA
import warnings


def forecast_arima(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Strategia 'ARIMA (Aggressive)'.
    Używa rzędu (5,1,0), aby wyłapać pęd (momentum) z ostatnich 5 świeczek,
    zamiast uśredniać wszystko do płaskiej linii.
    """
    # Wyciszamy wszystko co zbędne
    warnings.simplefilter('ignore')

    clean_series = series.dropna()
    if len(clean_series) < 30:
        return pd.Series([clean_series.iloc[-1]] * horizon)

    # 1. Konwersja na czysty numpy array float (kluczowe dla statsmodels)
    # Pozbywamy się indeksu czasowego, żeby biblioteka nie marudziła o luki w czasie
    values = clean_series.values.astype(float)

    # Logarytm dla stabilizacji wariancji
    log_values = np.log(values)

    try:
        # 2. Model AR(5) - patrzy na 5 kroków w tył (lepsze dla krypto niż (1,1,1))
        # trend='t' próbuje uchwycić liniowy trend wewnątrz próbki
        model = StatsARIMA(
            log_values,
            order=(5, 1, 0),
            trend='t',  # 't' = linear trend, pomaga uniknąć płaskiej linii
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        # method='innovations_mle' jest szybsza i stabilniejsza dla prostych arrayów
        model_fit = model.fit(method='innovations_mle')

        # 3. Prognoza
        forecast_log = model_fit.forecast(steps=horizon)

        # Odwrócenie logarytmu
        forecast_price = np.exp(forecast_log)

        return pd.Series(data=forecast_price)

    except Exception as e:
        print(f"CRITICAL ARIMA ERROR: {e}")
        # Jeśli model się wywali, zrób prostą projekcję liniową z ostatnich 2 punktów
        # żeby wykres nie był chamsko płaski
        try:
            p1 = values[-2]
            p2 = values[-1]
            diff = p2 - p1
            future = [p2 + (diff * (i + 1) * 0.5) for i in range(horizon)]  # 0.5 to tłumienie
            return pd.Series(data=future)
        except:
            return pd.Series([clean_series.iloc[-1]] * horizon)


def get_forecast_method():
    return {
        "key": "arima",
        "name": "ARIMA (Momentum)",
        "category": "Statistical Models",
        "forecast": forecast_arima,
        "description": "Model autoregresyjny (AR-5) nastawiony na wykrywanie krótkoterminowego pędu ceny. Ignoruje luki w czasie.",
        "color": "#ffaa00"
    }