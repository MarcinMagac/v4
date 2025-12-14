# core/indicators_lib.py
import pandas_ta as ta

# --- REJESTR WSKAŹNIKÓW ---
INDICATORS_REGISTRY = {}

def register_indicator(name, type='overlay', color='#ffffff', panel=None, viz_type='line'):
    """
    Dekorator rejestrujący wskaźnik.
    """
    def decorator(func):
        INDICATORS_REGISTRY[name] = {
            "func": func,
            "meta": {
                "key": name,
                "name": name, # Dodano pole name dla spójności
                "type": type,
                "color": color,
                "panel_id": panel,
                "viz_type": viz_type
            }
        }
        return func
    return decorator

# --- 1. WSKAŹNIKI NAKŁADANE (OVERLAYS) ---

@register_indicator("SMA 20", type='overlay', color='#2962ff')
def calc_sma_20(df): return df.ta.sma(length=20)

@register_indicator("SMA 50", type='overlay', color='#ff6d00')
def calc_sma_50(df): return df.ta.sma(length=50)

@register_indicator("SMA 200", type='overlay', color='#e91e63')
def calc_sma_200(df): return df.ta.sma(length=200)

@register_indicator("EMA 12", type='overlay', color='#2196f3')
def calc_ema_12(df): return df.ta.ema(length=12)

@register_indicator("EMA 26", type='overlay', color='#4caf50')
def calc_ema_26(df): return df.ta.ema(length=26)

@register_indicator("EMA 50", type='overlay', color='#ff6d00') # Dodano brakujące EMA 50 używane w main.py
def calc_ema_50(df): return df.ta.ema(length=50)

@register_indicator("Bollinger Bands", type='overlay', color='#9c27b0')
def calc_bbands(df):
    # Zwracamy środkową linię lub górną - tu przykład Upper
    bb = df.ta.bbands(length=20, std=2)
    return bb.iloc[:, 0] if bb is not None else None

@register_indicator("SuperTrend", type='overlay', color='#00e676')
def calc_supertrend(df):
    st = df.ta.supertrend(length=7, multiplier=3)
    return st.iloc[:, 0] if st is not None else None

@register_indicator("Parabolic SAR", type='overlay', color='#ffffff')
def calc_psar(df):
    psar = df.ta.psar()
    if psar is not None:
        # PSAR zwraca osobne kolumny dla long/short, trzeba je scalić
        return psar.iloc[:, 0].fillna(psar.iloc[:, 1])
    return None

# --- 2. WSKAŹNIKI PANELOWE (PANELS) ---

@register_indicator("RSI 14", type='panel', color='#7e57c2', panel='rsi_panel')
def calc_rsi(df):
    return df.ta.rsi(length=14)

# --- GRUPA MACD ---
@register_indicator("MACD", type='panel', color='#2962ff', panel='macd_panel')
def calc_macd_main(df):
    macd = df.ta.macd(fast=12, slow=26, signal=9)
    return macd.iloc[:, 0] if macd is not None else None

@register_indicator("MACD_Signal", type='panel', color='#ff6d00', panel='macd_panel')
def calc_macd_signal(df):
    macd = df.ta.macd(fast=12, slow=26, signal=9)
    return macd.iloc[:, 2] if macd is not None else None

@register_indicator("MACD_Hist", type='panel', color='#26a69a', panel='macd_panel', viz_type='histogram')
def calc_macd_hist(df):
    macd = df.ta.macd(fast=12, slow=26, signal=9)
    return macd.iloc[:, 1] if macd is not None else None

# --- PUBLICZNE API BIBLIOTEKI ---

def get_indicators_metadata():
    """Zwraca listę metadanych dla API."""
    return [item["meta"] for item in INDICATORS_REGISTRY.values()]

def calculate_indicator(name, df):
    """Wykonuje obliczenia dla danej nazwy."""
    if name in INDICATORS_REGISTRY:
        try:
            return INDICATORS_REGISTRY[name]["func"](df)
        except Exception as e:
            print(f"Error calculating {name}: {e}")
            return None
    return None