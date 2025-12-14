import pandas as pd
import numpy as np


def calculate_confidence(method_func, series: pd.Series, horizon: int, lookback_windows: int = 20) -> float:
    """
    Wykonuje 'Rolling Window Backtest'.
    Cofa się w czasie i sprawdza, czy strategia poprawnie przewidziała KIERUNEK ceny (Góra/Dół).

    Zwraca wynik 0-100%.
    """
    # Zabezpieczenie: potrzebujemy wystarczająco dużo danych (np. 50 świeczek + horyzont + lookback)
    if len(series) < 50 + horizon + lookback_windows:
        return 0.0

    hits = 0
    total = 0

    # Iterujemy wstecz, symulując, że jesteśmy w przeszłości
    # start_index = ostatni znany punkt, dla którego znamy przyszłość (horizon)
    last_possible_index = len(series) - horizon - 1
    start_index = last_possible_index
    end_index = max(last_possible_index - lookback_windows, 50)

    for i in range(start_index, end_index, -1):
        try:
            # 1. Trenujemy/karmimy strategię danymi TYLKO do punktu 'i' (nie podglądamy przyszłości)
            input_slice = series.iloc[:i + 1]
            current_price = series.iloc[i]

            # 2. Rzeczywista cena, która wystąpiła 'horizon' dni później
            actual_future_price = series.iloc[i + horizon]

            # 3. Co strategia myślała w tamtym momencie?
            forecast_series = method_func(input_slice, horizon=horizon)

            # Pobieramy ostatni punkt prognozy
            predicted_future_price = forecast_series.iloc[-1]

            # 4. Ocena: Czy przewidziała kierunek? (Directional Accuracy)
            actual_move = actual_future_price - current_price
            predicted_move = predicted_future_price - current_price

            # Jeśli oba ruchy są dodatnie LUB oba ujemne -> sukces
            if (actual_move > 0 and predicted_move > 0) or (actual_move < 0 and predicted_move < 0):
                hits += 1
            # Jeśli rynek stał w miejscu (zmiana < 0.1%), uznajemy remis (0.5 pkt)
            elif abs(actual_move) < (current_price * 0.001):
                hits += 0.5

            total += 1
        except Exception:
            continue

    if total == 0:
        return 0.0

    # Wynik w procentach
    return round((hits / total) * 100, 1)