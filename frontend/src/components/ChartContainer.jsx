import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import DrawingToolbar from './DrawingToolbar';
import { v4 as uuidv4 } from 'uuid';

const CONFIG = {
  layout: { background: { type: ColorType.Solid, color: '#0b0e11' }, textColor: '#848e9c', fontFamily: "'Inter', sans-serif" },
  grid: { vertLines: { color: '#181a20' }, horzLines: { color: '#181a20' } },
  timeScale: { timeVisible: true, secondsVisible: false, borderColor: '#2b3139' },
  crosshair: { mode: 1, vertLine: { width: 1, color: '#555', labelBackgroundColor: '#0b0e11' }, horzLine: { width: 1, color: '#555', labelBackgroundColor: '#0b0e11' } },
  handleScroll: { vertTouchDrag: false },
};

const ChartContainer = ({ data, appMode, onPriceUpdate }) => {
  const chartContainerRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const legendRef = useRef(null);
  const seriesRef = useRef({ candles: null, prediction: null, overlays: [], panels: [] });

  // --- STATE DLA DRAWING TOOLBOX ---
  const [activeTool, setActiveTool] = useState(null);
  const [drawings, setDrawings] = useState([]);
  const [currentDrawing, setCurrentDrawing] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [chartVersion, setChartVersion] = useState(0);

  // Load drawings
  useEffect(() => {
    const saved = localStorage.getItem('user_drawings');
    if (saved) setDrawings(JSON.parse(saved));
  }, []);

  // Save drawings
  useEffect(() => {
    localStorage.setItem('user_drawings', JSON.stringify(drawings));
  }, [drawings]);

  // --- 1. INICJALIZACJA WYKRESU ---
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      ...CONFIG,
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      rightPriceScale: { visible: true, borderColor: '#2b3139', scaleMargins: { top: 0.1, bottom: 0.0 } }
    });

    // Re-render SVG on zoom/scroll
    chart.timeScale().subscribeVisibleTimeRangeChange(() => {
        setChartVersion(v => v + 1);
    });

    const candleSeries = chart.addCandlestickSeries({ upColor: '#0ecb81', downColor: '#f6465d', borderVisible: false, wickUpColor: '#0ecb81', wickDownColor: '#f6465d' });
    const predSeries = chart.addLineSeries({ color: '#fcd535', lineWidth: 2, lineStyle: 2, title: 'AI Forecast', lastValueVisible: false });

    chartInstanceRef.current = chart;
    seriesRef.current.candles = candleSeries;
    seriesRef.current.prediction = predSeries;

    const handleResize = () => {
        if(chartContainerRef.current) {
            chart.applyOptions({ width: chartContainerRef.current.clientWidth, height: chartContainerRef.current.clientHeight });
            setChartVersion(v => v + 1);
        }
    };
    window.addEventListener('resize', handleResize);

    // Legend Update Logic
    chart.subscribeCrosshairMove(param => {
      if (!legendRef.current || !param.time) return;
      const candleData = param.seriesData.get(candleSeries);
      let html = '';
      if (candleData) html += `<div style="margin-bottom: 5px;"><span style="color:#eaecef; font-weight:bold">${candleData.close?.toFixed(2)}</span> <span style="color:#848e9c; font-size:10px">${new Date(param.time * 1000).toLocaleDateString()}</span></div>`;

      // Overlays (SMA, EMA)
      seriesRef.current.overlays.forEach(ov => {
          if (!ov.options().visible) return;
          const val = param.seriesData.get(ov);
          if (val !== undefined) html += `<span style="color:${ov.options().color}; margin-right:8px; font-weight:600; font-size: 10px;">${ov.options().title}:${val.value.toFixed(2)}</span>`;
      });

      // Panels (RSI, MACD)
      seriesRef.current.panels.forEach(panel => {
          if (!panel.series.options().visible) return;
          const val = param.seriesData.get(panel.series);
          if (val !== undefined) {
              const v = (val.value !== undefined) ? val.value : val;
              html += `<span style="color:${panel.color}; margin-right:8px; font-weight:600; font-size: 10px;">${panel.name}:${v.toFixed(2)}</span>`;
          }
      });

      legendRef.current.innerHTML = html;
    });

    return () => { window.removeEventListener('resize', handleResize); chart.remove(); };
  }, []);

  // --- 2. AKTUALIZACJA DANYCH (Full Logic Restored) ---
  useEffect(() => {
    if (!data || !chartInstanceRef.current) return;
    const chart = chartInstanceRef.current;

    // 2.1 History & Candles
    const history = (data.history || []).map(d => ({ ...d, time: parseInt(d.time) })).sort((a,b)=>a.time-b.time);
    seriesRef.current.candles.setData(history);

    if(history.length > 0 && onPriceUpdate) {
        const last = history[history.length-1];
        const prev = history[history.length > 1 ? history.length-2 : 0];
        onPriceUpdate({ lastPrice: last.close, change: last.close - prev.close, changePercent: ((last.close - prev.close)/prev.close)*100 });
    }

    // 2.2 AI Prediction
    if (appMode === 'lab' && data.predictions?.[0]) {
       const predData = Object.entries(data.predictions[0].forecast_values).map(([t,v]) => ({time: parseInt(t), value:v})).sort((a,b)=>a.time-b.time);
       seriesRef.current.prediction.setData(predData);
       seriesRef.current.prediction.applyOptions({ visible: true });
    } else {
       seriesRef.current.prediction.setData([]);
       seriesRef.current.prediction.applyOptions({ visible: false });
    }

    // 2.3 CLEANUP OLD INDICATORS
    seriesRef.current.overlays.forEach(s => chart.removeSeries(s));
    seriesRef.current.overlays = [];
    seriesRef.current.panels.forEach(p => chart.removeSeries(p.series));
    seriesRef.current.panels = [];

    // 2.4 MARKET MODE INDICATORS (Restored Logic)
    if (appMode === 'market') {
        // Overlays (SMA/EMA on main chart)
        if (data.technical_indicators) {
            data.technical_indicators.forEach(ind => {
                const line = chart.addLineSeries({ color: ind.color, lineWidth: 1, title: ind.name, lastValueVisible: false, priceLineVisible: false });
                line.setData(ind.data);
                seriesRef.current.overlays.push(line);
            });
        }

        // Panels (RSI/MACD separate panes)
        const panelsData = data.panels || [];
        const totalPanelsHeight = panelsData.length * 0.25; // 25% height per panel

        // Adjust main chart margin to make room for panels
        chart.priceScale('right').applyOptions({ scaleMargins: { top: 0.05, bottom: totalPanelsHeight } });

        panelsData.forEach((panel, index) => {
            const topMargin = (1 - totalPanelsHeight) + (index * 0.25);
            const bottomMargin = Math.max(0, totalPanelsHeight - ((index + 1) * 0.25));
            const uniqueScaleId = `scale_${panel.id}_${index}`;

            panel.series.forEach(s => {
                let series;
                const options = { color: s.color, title: s.name, priceScaleId: uniqueScaleId };

                if (s.type === 'histogram') {
                    series = chart.addHistogramSeries(options);
                    series.setData(s.data.map(d => ({ time: parseInt(d.time), value: d.value, color: d.value >= 0 ? '#26a69a' : '#ef5350' })));
                } else {
                    series = chart.addLineSeries({ ...options, lineWidth: 1 });
                    series.setData(s.data.map(d => ({time: parseInt(d.time), value: d.value})));
                }
                seriesRef.current.panels.push({ series, name: s.name, color: s.color });
            });

            // Configure the separate scale for this panel
            chart.priceScale(uniqueScaleId).applyOptions({
                autoScale: true,
                visible: true,
                borderVisible: true,
                borderColor: '#2b3139',
                scaleMargins: { top: topMargin, bottom: bottomMargin }
            });
        });
    } else {
        // Reset margins if not in market mode
        chart.priceScale('right').applyOptions({ scaleMargins: { top: 0.1, bottom: 0.0 } });
    }
  }, [data, appMode, onPriceUpdate]); // Dodane onPriceUpdate do dependency array


  // --- 3. LOGIKA RYSOWANIA (Drawing System) ---
  const getChartCoordinates = (e) => {
    const chart = chartInstanceRef.current;
    const series = seriesRef.current.candles;
    if (!chart || !series || !chartContainerRef.current) return null;

    const rect = chartContainerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const time = chart.timeScale().coordinateToTime(x);
    const price = series.coordinateToPrice(y);

    if (time === null || price === null) return null;
    return { time, price, x, y };
  };

  const handleSvgClick = (e) => {
    if (!activeTool) return;
    const coords = getChartCoordinates(e);
    if (!coords) return;

    if (!currentDrawing) {
      setCurrentDrawing({
        id: uuidv4(),
        type: activeTool,
        p1: { time: coords.time, price: coords.price },
        p2: { time: coords.time, price: coords.price },
      });
    } else {
      setDrawings([...drawings, { ...currentDrawing, p2: { time: coords.time, price: coords.price } }]);
      setCurrentDrawing(null);
    }
  };

  const handleSvgMouseMove = (e) => {
    if (!activeTool || !currentDrawing) return;
    const coords = getChartCoordinates(e);
    if (!coords) return;

    setCurrentDrawing(prev => ({
      ...prev,
      p2: { time: coords.time, price: coords.price }
    }));
  };

  // --- 4. RENDEROWANIE WARSTWY SVG ---
  const renderShape = (shape, isPreview = false) => {
    const chart = chartInstanceRef.current;
    const series = seriesRef.current.candles;
    if (!chart || !series) return null;

    const x1 = chart.timeScale().timeToCoordinate(shape.p1.time);
    const y1 = series.priceToCoordinate(shape.p1.price);
    const x2 = chart.timeScale().timeToCoordinate(shape.p2.time);
    const y2 = series.priceToCoordinate(shape.p2.price);

    if (x1 === null || y1 === null || x2 === null || y2 === null) return null;

    const style = { stroke: '#2962ff', strokeWidth: 2, opacity: isPreview ? 0.7 : 1 };

    if (shape.type === 'trendline') {
      return (
        <g key={shape.id}>
           <line x1={x1} y1={y1} x2={x2} y2={y2} {...style} />
           <circle cx={x1} cy={y1} r={3} fill="#fff" />
           <circle cx={x2} cy={y2} r={3} fill="#fff" />
        </g>
      );
    }
    else if (shape.type === 'horizontal') {
      return (
        <g key={shape.id}>
           <line x1={0} y1={y1} x2={chartContainerRef.current?.clientWidth || 2000} y2={y1} {...style} strokeDasharray="4" />
           <text x={chartContainerRef.current?.clientWidth - 50} y={y1 - 5} fill="#2962ff" fontSize="10">{shape.p1.price.toFixed(2)}</text>
        </g>
      );
    }
    return null;
  };

  return (
    <div className="chart-wrapper" style={{position:'relative', width:'100%', height:'100%'}}>
      <DrawingToolbar
        activeTool={activeTool}
        onSelectTool={setActiveTool}
        onClearAll={() => setDrawings([])}
        drawingsCount={drawings.length}
      />

      <div ref={chartContainerRef} style={{width: '100%', height: '100%'}} />

      <svg
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          zIndex: 10,
          pointerEvents: activeTool ? 'auto' : 'none',
          cursor: activeTool ? 'crosshair' : 'default'
        }}
        onClick={handleSvgClick}
        onMouseMove={handleSvgMouseMove}
      >
        {drawings.map(d => renderShape(d))}
        {currentDrawing && renderShape(currentDrawing, true)}
      </svg>

      <div ref={legendRef} className="chart-legend-floating"></div>
      <div className="watermark"><h1>{appMode === 'market' ? 'MARKET VIEW' : 'QUANT LAB'}</h1></div>
    </div>
  );
};
export default ChartContainer;