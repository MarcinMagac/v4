import pandas as pd
import numpy as np


def forecast_ma(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Prosta średnia krocząca.
    Zwraca serię wartości bez indeksu czasowego.
    """
    # Czyścimy dane z ewentualnych pustych miejsc
    clean_series = series.dropna()

    if clean_series.empty:
        return pd.Series([])

    # 1. Obliczenie średniej z ostatnich 7 punktów
    window = min(len(clean_series), 7)
    last_ma = clean_series.tail(window).mean()

    # 2. Tworzenie płaskiej linii w przyszłość
    # Zwracamy po prostu listę wartości
    forecast_values = [float(last_ma)] * horizon

    return pd.Series(data=forecast_values)


def get_forecast_method():
    return {
        "key": "simple_ma",
        "name": "Simple Moving Average",
        "category": "Basic",
        "forecast": forecast_ma,
        "description": "Prognozuje płaską linię na podstawie średniej."
    }