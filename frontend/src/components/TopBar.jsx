import AssetSelect from './AssetSelect';

const TopBar = ({
  appMode, setAppMode, ticker, setTicker, interval, setInterval, availableAssets, apiUsage,
  selectedIndicators, availableIndicators, toggleIndicator, showIndicators, setShowIndicators,
  selectedMethod, setSelectedMethod, availableMethods, handleFetch, aiStatus
}) => {
  const timeframes = [
    { value: '1min', label: '1M' }, { value: '5min', label: '5M' }, { value: '15min', label: '15M' },
    { value: '30min', label: '30M' }, { value: '1h', label: '1H' }, { value: '4h', label: '4H' },
    { value: '1day', label: '1D' }, { value: '1week', label: '1W' }
  ];

  return (
    <header className="topbar">
      <div style={{display:'flex', gap: 15, alignItems:'center', flex: 1}}>
          <div className="brand mobile-hide">MAGAC<span>LAB</span></div>
          <div className="mode-switcher">
              <button className={`btn-mode ${appMode === 'market' ? 'active' : ''}`} onClick={() => setAppMode('market')}>MARKET</button>
              <button className={`btn-mode ${appMode === 'lab' ? 'active' : ''}`} onClick={() => setAppMode('lab')}>LAB</button>
          </div>
      </div>
      <div className="controls-right-stack">
          <div className="control-row">
               <AssetSelect assets={availableAssets} selectedValue={ticker} onSelect={setTicker} />
              <div className="tf-mini-group">
                  {timeframes.map(tf => (
                    <button key={tf.value} className={`btn-tf-mini ${interval === tf.value ? 'active' : ''}`} onClick={() => setInterval(tf.value)}>{tf.label}</button>
                  ))}
              </div>
          </div>
          {appMode === 'market' && (
              <div className="control-row">
                  <div className="dropdown-container" style={{width:'100%'}}>
                      <button className="btn-dropdown" onClick={()=>setShowIndicators(!showIndicators)}>WSKAŹNIKI {selectedIndicators.length>0 && `(${selectedIndicators.length})`}</button>
                      {showIndicators && <div className="menu-backdrop" onClick={()=>setShowIndicators(false)}></div>}
                      {showIndicators && (
                      <div className="dropdown-menu">
                          <div className="mobile-menu-label">Techniczne</div>
                          {availableIndicators.map(ind => (
                          <label key={ind.key} className="checkbox-item"><input type="checkbox" checked={selectedIndicators.includes(ind.key)} onChange={()=>toggleIndicator(ind.key)}/> {ind.key}</label>
                          ))}
                      </div>
                      )}
                  </div>
              </div>
          )}
          {appMode === 'lab' && (
              <div className="control-row" style={{gap: 5}}>
                  <select className="select-field model-select" value={selectedMethod} onChange={e=>setSelectedMethod(e.target.value)}>
                      {availableMethods.map(m=><option key={m.key} value={m.key}>{m.name}</option>)}
                  </select>
                  <button className="btn-action btn-run" onClick={()=>handleFetch(true)}>{aiStatus === 'Thinking...' ? '...' : 'RUN'}</button>
              </div>
          )}
      </div>
      <div className="api-widget mobile-hide" style={{marginLeft:'15px'}}>
          <div className="api-text">API: {apiUsage.percent}%</div>
          <div className="api-bar-bg"><div className="api-bar-fill" style={{width:`${apiUsage.percent}%`, background: apiUsage.percent>80?'#f6465d':'#0ecb81'}}></div></div>
      </div>
    </header>
  );
};
export default TopBar;