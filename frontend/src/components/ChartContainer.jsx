import { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

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

  useEffect(() => {
    if (!chartContainerRef.current) return;
    const chart = createChart(chartContainerRef.current, { ...CONFIG, width: chartContainerRef.current.clientWidth, height: chartContainerRef.current.clientHeight, rightPriceScale: { visible: true, borderColor: '#2b3139', scaleMargins: { top: 0.1, bottom: 0.0 } } });
    const candleSeries = chart.addCandlestickSeries({ upColor: '#0ecb81', downColor: '#f6465d', borderVisible: false, wickUpColor: '#0ecb81', wickDownColor: '#f6465d' });
    const predSeries = chart.addLineSeries({ color: '#fcd535', lineWidth: 2, lineStyle: 2, title: 'AI Forecast', lastValueVisible: false });

    chartInstanceRef.current = chart;
    seriesRef.current.candles = candleSeries;
    seriesRef.current.prediction = predSeries;

    const handleResize = () => { if(chartContainerRef.current) chart.applyOptions({ width: chartContainerRef.current.clientWidth, height: chartContainerRef.current.clientHeight }); };
    window.addEventListener('resize', handleResize);

    chart.subscribeCrosshairMove(param => {
      if (!legendRef.current || !param.time) return;
      const candleData = param.seriesData.get(candleSeries);
      let html = '';
      if (candleData) html += `<div style="margin-bottom: 5px;"><span style="color:#eaecef; font-weight:bold">${candleData.close?.toFixed(2)}</span> <span style="color:#848e9c; font-size:10px">${new Date(param.time * 1000).toLocaleDateString()}</span></div>`;
      seriesRef.current.overlays.forEach(ov => { if (!ov.options().visible) return; const val = param.seriesData.get(ov); if (val !== undefined) html += `<span style="color:${ov.options().color}; margin-right:8px; font-weight:600; font-size: 10px;">${ov.options().title}:${val.value.toFixed(2)}</span>`; });
      seriesRef.current.panels.forEach(panel => { if (!panel.series.options().visible) return; const val = param.seriesData.get(panel.series); if (val !== undefined) { const v = (val.value !== undefined) ? val.value : val; html += `<span style="color:${panel.color}; margin-right:8px; font-weight:600; font-size: 10px;">${panel.name}:${v.toFixed(2)}</span>`; } });
      legendRef.current.innerHTML = html;
    });
    return () => { window.removeEventListener('resize', handleResize); chart.remove(); };
  }, []);

  useEffect(() => {
    if (!data || !chartInstanceRef.current) return;
    const chart = chartInstanceRef.current;
    const history = (data.history || []).map(d => ({ ...d, time: parseInt(d.time) })).sort((a,b)=>a.time-b.time);
    seriesRef.current.candles.setData(history);

    if(history.length > 0 && onPriceUpdate) {
        const last = history[history.length-1];
        const prev = history[history.length > 1 ? history.length-2 : 0];
        onPriceUpdate({ lastPrice: last.close, change: last.close - prev.close, changePercent: ((last.close - prev.close)/prev.close)*100 });
    }

    if (appMode === 'lab' && data.predictions?.[0]) {
       const predData = Object.entries(data.predictions[0].forecast_values).map(([t,v]) => ({time: parseInt(t), value:v})).sort((a,b)=>a.time-b.time);
       seriesRef.current.prediction.setData(predData);
       seriesRef.current.prediction.applyOptions({ visible: true });
    } else {
       seriesRef.current.prediction.setData([]);
       seriesRef.current.prediction.applyOptions({ visible: false });
    }

    seriesRef.current.overlays.forEach(s => chart.removeSeries(s));
    seriesRef.current.overlays = [];
    seriesRef.current.panels.forEach(p => chart.removeSeries(p.series));
    seriesRef.current.panels = [];

    if (appMode === 'market') {
        if (data.technical_indicators) {
            data.technical_indicators.forEach(ind => {
                const line = chart.addLineSeries({ color: ind.color, lineWidth: 1, title: ind.name, lastValueVisible: false, priceLineVisible: false });
                line.setData(ind.data);
                seriesRef.current.overlays.push(line);
            });
        }
        const panelsData = data.panels || [];
        const totalPanelsHeight = panelsData.length * 0.25;
        chart.priceScale('right').applyOptions({ scaleMargins: { top: 0.05, bottom: totalPanelsHeight } });

        panelsData.forEach((panel, index) => {
            const topMargin = (1 - totalPanelsHeight) + (index * 0.25);
            const bottomMargin = Math.max(0, totalPanelsHeight - ((index + 1) * 0.25));
            const uniqueScaleId = `scale_${panel.id}_${index}`;
            panel.series.forEach(s => {
                let series;
                const options = { color: s.color, title: s.name, priceScaleId: uniqueScaleId };
                if (s.type === 'histogram') { series = chart.addHistogramSeries(options); series.setData(s.data.map(d => ({ time: parseInt(d.time), value: d.value, color: d.value >= 0 ? '#26a69a' : '#ef5350' }))); }
                else { series = chart.addLineSeries({ ...options, lineWidth: 1 }); series.setData(s.data.map(d => ({time: parseInt(d.time), value: d.value}))); }
                seriesRef.current.panels.push({ series, name: s.name, color: s.color });
            });
            chart.priceScale(uniqueScaleId).applyOptions({ autoScale: true, visible: true, borderVisible: true, borderColor: '#2b3139', scaleMargins: { top: topMargin, bottom: bottomMargin } });
        });
    } else {
        chart.priceScale('right').applyOptions({ scaleMargins: { top: 0.1, bottom: 0.0 } });
    }
  }, [data, appMode]);

  return (
    <div className="chart-wrapper" style={{position:'relative', width:'100%', height:'100%'}}>
      <div ref={chartContainerRef} style={{width: '100%', height: '100%'}} />
      <div ref={legendRef} className="chart-legend-floating"></div>
      <div className="watermark"><h1>{appMode === 'market' ? 'MARKET VIEW' : 'QUANT LAB'}</h1></div>
    </div>
  );
};
export default ChartContainer;