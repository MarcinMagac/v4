import os

# 1. Wyciszamy logi TensorFlow (musi być PRZED importem tf)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 3 = FATAL only (wycisza INFO i WARNING)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Wyłącza dodatkowe optymalizacje Intela, które czasem śmiecą w logach

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input  # <--- Dodano Input


def forecast_lstm(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Strategia LSTM (Deep Learning).
    Wersja poprawiona pod najnowsze API Keras/TensorFlow.
    """
    # 1. Przygotowanie danych
    clean_series = series.dropna()
    values = clean_series.values.reshape(-1, 1)

    LOOK_BACK = 30
    # Sprawdzamy czy mamy dość danych (30 na historię + 20 na rozruch)
    if len(values) < LOOK_BACK + 20:
        return pd.Series([clean_series.iloc[-1]] * horizon)

    # 2. Skalowanie (Neural Networks wymagają danych 0-1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(values)

    # 3. Tworzenie sekwencji treningowych
    X_train, y_train = [], []
    for i in range(LOOK_BACK, len(scaled_data)):
        X_train.append(scaled_data[i - LOOK_BACK:i, 0])
        y_train.append(scaled_data[i, 0])

    X_train, y_train = np.array(X_train), np.array(y_train)
    # Reshape [próbki, kroki, cechy]
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # 4. Budowa Modelu (Nowa składnia bez ostrzeżeń)
    model = Sequential()

    # FIX: Jawna warstwa wejściowa zamiast argumentu input_shape
    model.add(Input(shape=(LOOK_BACK, 1)))

    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    # 5. Trenowanie (Suppress output with verbose=0)
    model.fit(X_train, y_train, epochs=15, batch_size=32, verbose=0)

    # 6. Generowanie Prognozy
    current_batch = scaled_data[-LOOK_BACK:].reshape(1, LOOK_BACK, 1)
    predicted_scaled = []

    for _ in range(horizon):
        current_pred = model.predict(current_batch, verbose=0)
        predicted_scaled.append(current_pred[0, 0])

        current_pred_reshaped = current_pred.reshape(1, 1, 1)
        current_batch = np.append(current_batch[:, 1:, :], current_pred_reshaped, axis=1)

    # 7. Odwrócenie skalowania
    predictions = scaler.inverse_transform(np.array(predicted_scaled).reshape(-1, 1))

    return pd.Series(data=predictions.flatten())


def get_forecast_method():
    return {
        "key": "lstm_neural",
        "name": "LSTM (Deep Learning)",
        "category": "AI Models",
        "forecast": forecast_lstm,
        "description": "Sieć neuronowa. Wymaga min. 50 świec.",
        "color": "#9c27b0"
    }