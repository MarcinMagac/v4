import { useEffect, useState } from 'react';
import './App.css';
import './mobile.css';
import TopBar from './components/TopBar';
import ChartContainer from './components/ChartContainer';

const API_URL = "http://127.0.0.1:8000";

// Helper do formatowania dużych liczb (np. 1.2M)
const formatVol = (val) => {
  if (!val) return '0';
  if (val >= 1000000) return (val / 1000000).toFixed(2) + 'M';
  if (val >= 1000) return (val / 1000).toFixed(2) + 'K';
  return val.toFixed(0);
};

const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => { const handler = setTimeout(() => setDebouncedValue(value), delay); return () => clearTimeout(handler); }, [value, delay]);
  return debouncedValue;
};

function App() {
  const [appMode, setAppMode] = useState('market');
  const [ticker, setTicker] = useState('BTC/USD');
  const [interval, setInterval] = useState('1day');
  const [selectedIndicators, setSelectedIndicators] = useState([]);
  const debouncedIndicators = useDebounce(selectedIndicators, 100);
  const [showIndicators, setShowIndicators] = useState(false);
  const [showSR, setShowSR] = useState(false);
  const [showVolume, setShowVolume] = useState(true);
  const [selectedMethod, setSelectedMethod] = useState('simple_ma');
  const [horizon, setHorizon] = useState(14);
  const [aiStatus, setAiStatus] = useState('Idle');
  const [marketData, setMarketData] = useState({ lastPrice: 0, change: 0, changePercent: 0 });
  const [apiUsage, setApiUsage] = useState({ percent: 0, used: 0, limit: 800 });
  const [cachedData, setCachedData] = useState(null);
  const [availableAssets, setAvailableAssets] = useState([{ value: "BTC/USD", label: "Bitcoin", type: "crypto" }]);
  const [availableMethods, setAvailableMethods] = useState([{ key: 'simple_ma', name: 'Simple MA' }]);
  const [availableIndicators, setAvailableIndicators] = useState([]);
  const [predictionHistory, setPredictionHistory] = useState([]);

  useEffect(() => {
    const init = async () => {
      try {
        const [assets, methods, indicators] = await Promise.all([
          fetch(`${API_URL}/assets`).then(r=>r.json()),
          fetch(`${API_URL}/methods`).then(r=>r.json()),
          fetch(`${API_URL}/indicators`).then(r=>r.json())
        ]);
        if(assets.assets) setAvailableAssets(assets.assets);
        if(methods.methods) { setAvailableMethods(methods.methods); setSelectedMethod(methods.methods[0].key); }
        if(indicators.indicators) setAvailableIndicators(indicators.indicators);
      } catch(e) { console.error(e); }
    };
    init();
  }, []);

  const handleFetch = async (isForecast = false) => {
    if (isForecast) setAiStatus('Thinking...');
    try {
      const methodList = isForecast ? [selectedMethod] : [];
      const payload = { ticker, method_keys: methodList, horizon: parseInt(horizon), indicators: debouncedIndicators, interval };
      const res = await fetch(`${API_URL}/predict`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
      const data = await res.json();
      if (data.api_usage) setApiUsage(data.api_usage);
      setCachedData(data);

      if (isForecast && data.predictions && data.predictions.length > 0) {
          const newPrediction = {
              id: Date.now(),
              timestamp: Date.now(),
              model: selectedMethod,
              data: data.predictions[0]
          };
          setPredictionHistory(prev => [...prev, newPrediction]);
      }

      if (isForecast) setAiStatus('Done');
    } catch (e) { console.error(e); setAiStatus('Error'); }
  };

  useEffect(() => {
      if(ticker) {
          handleFetch(false);
          setPredictionHistory([]);
      }
  }, [ticker, interval]);

  useEffect(() => { if(ticker) handleFetch(false); }, [debouncedIndicators]);

  const toggleIndicator = (k) => setSelectedIndicators(prev => prev.includes(k) ? prev.filter(i=>i!==k) : [...prev, k]);

  // --- LOGIKA VOLUMENU (NAPRAWIONA) ---
  // Sprawdzamy czy w ogóle mamy wolumen w danych (czy suma > 0)
  const hasVolume = cachedData?.history?.some(d => d.volume > 0) || false;
  // Pobieramy wartość z ostatniej świeczki do wyświetlenia w nagłówku
  const currentVolume = cachedData?.history?.[cachedData.history.length - 1]?.volume || 0;
  // -------------------------------------

  return (
    <div className="app-container">
      <TopBar
        appMode={appMode} setAppMode={setAppMode}
        ticker={ticker} setTicker={setTicker}
        interval={interval} setInterval={setInterval}
        availableAssets={availableAssets}
        apiUsage={apiUsage}
        selectedIndicators={selectedIndicators}
        availableIndicators={availableIndicators}
        toggleIndicator={toggleIndicator}
        showIndicators={showIndicators} setShowIndicators={setShowIndicators}
        showSR={showSR} setShowSR={setShowSR}
        showVolume={showVolume} setShowVolume={setShowVolume}
        selectedMethod={selectedMethod} setSelectedMethod={setSelectedMethod}
        availableMethods={availableMethods}
        handleFetch={handleFetch}
        aiStatus={aiStatus}
        // Przekazanie horyzontu (było w poprzednim kroku, dodaję dla pewności)
        horizon={horizon} setHorizon={setHorizon}
      />

      <div className="market-header">
        <div className="metric">PRICE: <span className={marketData.change>=0?'up':'down'}>{marketData.lastPrice.toFixed(2)}</span></div>
        <div className="metric">CHANGE: <span className={marketData.change>=0?'up':'down'}>{marketData.change.toFixed(2)} ({marketData.changePercent.toFixed(2)}%)</span></div>

        {/* NAPRAWIONE WYSWIETLANIE WOLUMENU */}
        <div className="metric">
            VOLUME: <span style={{color: '#848e9c', fontWeight: 'bold'}}>
                {hasVolume ? formatVol(currentVolume) : "NO VOLUME"}
            </span>
        </div>

        {appMode === 'lab' && (
          <div style={{marginLeft:'auto', display:'flex', gap:'15px', alignItems:'center'}}>
             {cachedData?.predictions?.[0]?.confidence_score !== undefined && (
                <div className="metric" style={{
                    color: cachedData.predictions[0].confidence_score >= 60 ? '#0ecb81' :
                           cachedData.predictions[0].confidence_score >= 45 ? '#fcd535' : '#f6465d',
                    border: '1px solid #2b3139',
                    padding: '2px 8px',
                    borderRadius: '4px'
                }}>
                  CONFIDENCE: {cachedData.predictions[0].confidence_score}%
                </div>
             )}
             <div className="metric" style={{color: '#fcd535'}}>AI: {aiStatus}</div>
          </div>
        )}
      </div>

      <main className="main-content">
        <ChartContainer
            data={cachedData}
            appMode={appMode}
            onPriceUpdate={setMarketData}
            predictionHistory={predictionHistory}
            showSR={showSR}
            // KLUCZOWE: Jeśli brak danych (hasVolume=false), wymuszamy ukrycie serii na wykresie
            showVolume={showVolume && hasVolume}
        />
      </main>
    </div>
  );
}
export default App;