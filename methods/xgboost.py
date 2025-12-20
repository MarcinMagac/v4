import pandas as pd
import numpy as np

try:
    import xgboost as xgb
    from xgboost import XGBRegressor
except ImportError:
    xgb = None

from core.logger import log


def forecast_xgboost_strategy(series: pd.Series, horizon: int) -> pd.Series:
    """
    Strategia XGBoost (Returns Regression). Bez emotikon.
    """

    log(f"[XGBoost] Uruchamiam metode. Horyzont: {horizon} dni.")

    if xgb is None:
        log("[XGBoost] BLAD: Brak biblioteki 'xgboost'. Zainstaluj ja: pip install xgboost")
        return pd.Series([series.iloc[-1]] * horizon)

    # 1. Przygotowanie danych
    log("[XGBoost] Przetwarzanie danych historycznych...")

    returns = series.pct_change().dropna()

    if len(returns) < 30:
        log(f"[XGBoost] Za malo danych ({len(returns)}). Wymagane min. 30. Zwracam linie plaska.")
        return pd.Series([series.iloc[-1]] * horizon)

    WINDOW_SIZE = 15
    values = returns.values
    X, y = [], []

    for i in range(WINDOW_SIZE, len(values)):
        X.append(values[i - WINDOW_SIZE:i])
        y.append(values[i])

    X = np.array(X)
    y = np.array(y)

    log(f"[XGBoost] Utworzono zbior treningowy: {len(X)} probek.")

    # 2. Trening
    log("[XGBoost] Trenowanie modelu (moze to chwile potrwac)...")

    model = XGBRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=3,
        n_jobs=-1,
        objective='reg:squarederror',
        random_state=42
    )

    model.fit(X, y)
    log("[XGBoost] Model wytrenowany. Rozpoczynam predykcje...")

    # 3. Predykcja
    predicted_returns = []
    current_input = values[-WINDOW_SIZE:]

    for i in range(horizon):
        if i > 0 and i % 10 == 0:
            log(f"[XGBoost] Obliczono dzien {i}/{horizon}...")

        pred_return = model.predict(current_input.reshape(1, -1))[0]
        pred_return = np.clip(pred_return, -0.15, 0.15)

        predicted_returns.append(pred_return)
        current_input = np.append(current_input[1:], pred_return)

    # 4. Rekonstrukcja
    log("[XGBoost] Rekonstrukcja cen z przewidzianych zwrotow...")

    last_price = series.iloc[-1]
    predicted_prices = []
    current_price = last_price

    for ret in predicted_returns:
        next_price = current_price * (1 + ret)
        if next_price < 0: next_price = 0
        predicted_prices.append(next_price)
        current_price = next_price

    log("[XGBoost] Zakonczono sukcesem. Zwracam wynik.")
    return pd.Series(predicted_prices)


def get_forecast_method():
    return {
        "key": "xgboost_strategy",
        "name": "XGBoost (ML Regression)",
        "category": "Machine Learning",
        "forecast": forecast_xgboost_strategy,
        "description": "Deterministyczny model Gradient Boosting z podgladem na zywo.",
        "color": "#FF8C00"
    }