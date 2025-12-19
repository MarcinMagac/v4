import pandas as pd
import numpy as np
import warnings
import os

# Wyciszenie logów TensorFlow (żeby nie śmiecił w konsoli)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Input
    from tensorflow.keras.callbacks import EarlyStopping
    import tensorflow as tf

    HAS_DL = True
except ImportError:
    HAS_DL = False


def forecast_lstm(series: pd.Series, horizon: int = 7) -> pd.Series:
    """
    Strategia 'Vanilla LSTM'.
    Wersja zoptymalizowana pod nowsze API Keras (używa warstwy Input).
    """
    if not HAS_DL:
        print("Brak bibliotek Deep Learning. Zainstaluj: pip install tensorflow scikit-learn")
        return pd.Series([series.iloc[-1]] * horizon)

    # 1. Przygotowanie danych
    clean_series = series.dropna()
    if len(clean_series) < 60:
        return pd.Series([clean_series.iloc[-1]] * horizon)

    # Reset indeksu i wyciągnięcie wartości (float32 dla TensorFlow)
    values = clean_series.values.reshape(-1, 1).astype('float32')

    # Skalowanie do zakresu 0-1
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(values)

    # 2. Parametry
    look_back = 20
    if len(values) < (look_back + 20):
        look_back = 5

    # Tworzenie zbioru X, y
    X, y = [], []
    for i in range(look_back, len(scaled_data)):
        X.append(scaled_data[i - look_back:i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    # Reshape pod LSTM: [samples, time steps, features]
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # 3. Budowa Modelu (Modern Keras Style)
    tf.random.set_seed(42)
    np.random.seed(42)

    model = Sequential()

    # --- FIX: Jawna warstwa wejściowa eliminuje Warning ---
    model.add(Input(shape=(look_back, 1)))
    # -----------------------------------------------------

    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    # 4. Trening z zabezpieczeniem (Early Stopping)
    early_stop = EarlyStopping(monitor='loss', patience=3, restore_best_weights=True)

    # verbose=0 sprawia, że trening jest "cichy"
    model.fit(X, y, epochs=25, batch_size=16, verbose=0, callbacks=[early_stop])

    # 5. Prognoza rekurencyjna
    forecast_scaled = []
    current_batch = scaled_data[-look_back:].reshape((1, look_back, 1))

    for _ in range(horizon):
        current_pred = model.predict(current_batch, verbose=0)[0]
        forecast_scaled.append(current_pred)

        # Aktualizujemy batch
        current_pred_reshaped = current_pred.reshape((1, 1, 1))
        current_batch = np.append(current_batch[:, 1:, :], current_pred_reshaped, axis=1)

    # 6. Odwrócenie skalowania
    forecast_values = scaler.inverse_transform(np.array(forecast_scaled).reshape(-1, 1))

    return pd.Series(data=forecast_values.flatten())


def get_forecast_method():
    return {
        "key": "lstm_vanilla",
        "name": "Vanilla LSTM (Deep Learning)",
        "category": "Deep Learning",
        "forecast": forecast_lstm,
        "description": "Sieć neuronowa LSTM. Uczy się sekwencji czasowych. Stosuje normalizację danych i rekurencyjną predykcję.",
        "color": "#ff1493"  # DeepPink
    }