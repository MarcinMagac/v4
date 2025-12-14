import uvicorn
import os
import math
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.registry import MethodRegistry
from core.data_client import client as data_client
from schemas import ForecastRequest, PredictionResponse, ForecastResult, ChartPanel, IndicatorSeriesDef
from core.indicators_lib import calculate_indicator, get_indicators_metadata
from core.backtester import calculate_confidence

app = FastAPI(title="Fintech Engine", version="v32.0_FIXED_TIME")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METHODS_DIR = os.path.join(BASE_DIR, "methods")
registry = MethodRegistry(METHODS_DIR)

INTERVAL_SECONDS = {
    "1min": 60,
    "5min": 300,
    "15min": 900,
    "30min": 1800,
    "45min": 2700,
    "1h": 3600,
    "2h": 7200,
    "4h": 14400,
    "1day": 86400,
    "1week": 604800,
    "1month": 2592000
}


@app.on_event("startup")
def startup_event():
    registry.load_methods()


@app.get("/assets")
def list_assets():
    return {"assets": data_client.get_all_assets()}


@app.get("/methods")
def list_methods():
    methods = registry.all_methods()
    return {"count": len(methods), "methods": [{"key": m.key, "name": m.name, "category": m.category} for m in methods]}


@app.get("/indicators")
def list_indicators():
    meta = get_indicators_metadata()
    filtered = [m for m in meta if "_Signal" not in m['key'] and "_Hist" not in m['key']]
    return {"count": len(filtered), "indicators": [{"key": m['key']} for m in filtered]}


def format_ta_series(series):
    if series is None or series.empty: return []
    try:
        timestamps = series.index.astype('int64') // 10 ** 9
        values = series.values
        formatted = [{"time": int(t), "value": float(v)} for t, v in zip(timestamps, values) if not math.isnan(v)]
        return sorted(formatted, key=lambda x: x['time'])
    except:
        return []


@app.post("/predict", response_model=PredictionResponse)
def generate_prediction(request: ForecastRequest):
    ticker = request.ticker
    interval = request.interval
    safe_horizon = max(request.horizon, 5)

    print(f"[API] Analiza: {ticker} ({interval}) | Horyzont: {safe_horizon}")

    try:
        df_ohlc = data_client.fetch_series(ticker, interval=interval, outputsize=5000)
        if df_ohlc.empty:
            raise Exception("Otrzymano pusty DataFrame z API")
        close_series = df_ohlc["close"]
    except Exception as e:
        print(f"[API ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Błąd danych: {str(e)}")

    raw_indicators = {}
    meta_lookup = {m['key']: m for m in get_indicators_metadata()}

    if request.indicators:
        for ind_name in request.indicators:
            try:
                res = calculate_indicator(ind_name, df_ohlc)
                if res is not None: raw_indicators[ind_name] = res
                if ind_name == "MACD":
                    raw_indicators["MACD_Signal"] = calculate_indicator("MACD_Signal", df_ohlc)
                    raw_indicators["MACD_Hist"] = calculate_indicator("MACD_Hist", df_ohlc)
            except:
                pass

    final_overlays = []
    panels_map = {}

    for name, series in raw_indicators.items():
        meta = meta_lookup.get(name, {"type": "overlay", "color": "#ccc"})
        formatted = format_ta_series(series)
        if not formatted: continue

        obj = {
            "name": name,
            "type": meta.get("viz_type", "line"),
            "color": meta.get("color", "#fff"),
            "data": formatted
        }

        if meta["type"] == "overlay":
            final_overlays.append(obj)
        elif meta["type"] == "panel":
            pid = meta.get("panel_id", "default")
            if pid not in panels_map: panels_map[pid] = []
            panels_map[pid].append(obj)

    final_panels = []
    for pid, slist in panels_map.items():
        final_panels.append(ChartPanel(id=pid, height=160, series=slist))

    results = []
    step = INTERVAL_SECONDS.get(interval, 86400)
    last_timestamp = int(df_ohlc.index[-1].timestamp())

    for key in request.method_keys:
        method = registry.get_by_key(key)
        if not method: continue

        try:
            confidence = calculate_confidence(method.func, close_series, safe_horizon)
            fc = method.func(close_series, horizon=safe_horizon)

            if len(fc) < 2:
                print(f"[AI WARNING] Metoda {method.name} zwróciła tylko {len(fc)} punktów!")

            values = fc.values
            fc_dict = {}

            for i in range(len(values)):
                if i >= safe_horizon: break

                next_ts = last_timestamp + ((i + 1) * step)
                fc_dict[str(next_ts)] = float(values[i])

            results.append(ForecastResult(
                method_name=method.name,
                forecast_values=fc_dict,
                confidence_score=confidence
            ))
            print(f"[AI] Sukces: {method.name} | Pewność: {confidence}% | Punktów: {len(fc_dict)}")

        except Exception as e:
            print(f"[AI CRITICAL] Błąd metody {key}: {e}")
            continue

    temp = df_ohlc.reset_index()
    temp['time'] = temp['datetime'].astype('int64') // 10 ** 9
    history = temp[['time', 'open', 'high', 'low', 'close', 'volume']].to_dict('records')

    return PredictionResponse(
        ticker=ticker,
        status="Success",
        history=history,
        predictions=results,
        technical_indicators=final_overlays,
        panels=final_panels,
        api_usage=data_client.get_quota()
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)