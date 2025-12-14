from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class ForecastRequest(BaseModel):
    ticker: str
    method_keys: List[str]
    horizon: int = 7
    indicators: List[str] = []
    interval: str = "1day"

class ForecastResult(BaseModel):
    method_name: str
    forecast_values: Dict[str, float]

class Candle(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float

class ApiUsage(BaseModel):
    limit: int
    used: int
    remaining: int
    percent: float

class IndicatorSeriesDef(BaseModel):
    name: str
    type: str
    color: str
    data: List[Dict[str, Any]]

class ChartPanel(BaseModel):
    id: str
    height: int
    series: List[IndicatorSeriesDef]

class PredictionResponse(BaseModel):
    ticker: str
    history: List[Candle]
    predictions: List[ForecastResult]
    technical_indicators: List[IndicatorSeriesDef] = []
    panels: List[ChartPanel] = []
    status: str
    api_usage: Optional[ApiUsage] = None