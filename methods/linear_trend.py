import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def forecast_linear(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Rysuje linię trendu (Regresja Liniowa).
    """
    clean_series = series.dropna()
    if len(clean_series) < 2:
        return pd.Series([])

    # Uczymy się na ostatnich 100 punktach
    lookback = min(len(clean_series), 100)
    recent_data = clean_series.tail(lookback)

    # X to po prostu numery [0, 1, 2...]
    X = np.array(range(len(recent_data))).reshape(-1, 1)
    y = recent_data.values

    model = LinearRegression()
    model.fit(X, y)

    # Przewidujemy kolejne punkty: N+1, N+2...
    last_x = X[-1][0]
    future_X = np.array(range(last_x + 1, last_x + 1 + horizon)).reshape(-1, 1)

    forecast_values = model.predict(future_X)

    # Zwracamy same wartości jako float
    return pd.Series(data=forecast_values.flatten())


def get_forecast_method():
    return {
        "key": "linear_trend",
        "name": "Linear Trend (AI)",
        "category": "Machine Learning",
        "forecast": forecast_linear,
        "description": "Wyznacza linię trendu matematycznego."
    }