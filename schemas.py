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
    confidence_score: Optional[float] = None  # <--- [DODAJ TO POLE]

class IndicatorSeriesDef(BaseModel):
    name: str
    type: str
    color: str
    data: List[Dict[str, Any]]
    panel_id: Optional[str] = None

class ChartPanel(BaseModel):
    id: str
    height: int
    series: List[IndicatorSeriesDef]

class PredictionResponse(BaseModel):
    ticker: str
    status: str
    history: List[Dict[str, float]]
    predictions: List[ForecastResult]
    technical_indicators: List[IndicatorSeriesDef]
    panels: List[ChartPanel]
    api_usage: Dict[str, Any]