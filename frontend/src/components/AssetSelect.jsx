import { useEffect, useRef, useState } from 'react';
import '../App.css';

const AssetSelect = ({ assets, selectedValue, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const wrapperRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      requestAnimationFrame(() => inputRef.current.focus());
    }
    if (!isOpen) setQuery("");
  }, [isOpen]);

  const getFilteredAssets = () => {
    if (!assets || assets.length === 0) return [];
    if (!query) return assets.slice(0, 50);

    const lowerQuery = query.toLowerCase();
    const results = [];
    for (let i = 0; i < assets.length; i++) {
      const item = assets[i];
      const label = item.label ? item.label.toLowerCase() : "";
      const symbol = item.symbol ? item.symbol.toLowerCase() : "";

      if (label.includes(lowerQuery) || symbol.includes(lowerQuery)) {
        results.push(item);
        if (results.length >= 50) break;
      }
    }
    return results;
  };

  const filteredAssets = getFilteredAssets();

  const getDisplayLabel = () => {
    const found = assets.find(a => a.symbol === selectedValue);
    if (!found) return selectedValue;
    return found.label
      .replace("CRYPTO | ", "")
      .replace("STOCK US | ", "")
      .replace("STOCK PL | ", "")
      .replace("STOCK | ", "");
  };

  return (
    <div className="custom-select-wrapper" ref={wrapperRef}>
      <div className="custom-select-trigger" onClick={() => setIsOpen(!isOpen)}>
        <span className="selected-text">{getDisplayLabel()}</span>
        <span className="arrow">▼</span>
      </div>

      {isOpen && (
        <div className="custom-select-dropdown">
          <div
            className="search-box-container"
            onClick={(e) => e.stopPropagation()}
          >
            <input
              ref={inputRef}
              type="text"
              className="asset-search-input"
              placeholder="Szukaj..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              autoComplete="off"
            />
            {query && (
              <button
                className="btn-clear-search"
                onClick={(e) => { e.stopPropagation(); setQuery(""); inputRef.current.focus(); }}
              >
                ×
              </button>
            )}
          </div>

          <div className="assets-list-scroll">
            {filteredAssets.length > 0 ? (
              filteredAssets.map((asset) => (
                <div
                  key={asset.symbol}
                  className={`asset-option ${asset.symbol === selectedValue ? 'selected' : ''}`}
                  onClick={() => {
                    onSelect(asset.symbol);
                    setIsOpen(false);
                  }}
                >
                  <span className={`badge ${asset.type === 'crypto' ? 'badge-crypto' : 'badge-stock'}`}>
                    {asset.type === 'crypto' ? 'CRYPTO' : 'STOCK'}
                  </span>
                  <span className="asset-name">
                    {asset.label
                      .replace("CRYPTO | ", "")
                      .replace("STOCK US | ", "")
                      .replace("STOCK PL | ", "")
                      .replace("STOCK | ", "")}
                  </span>
                </div>
              ))
            ) : (
              <div className="no-results">Brak wyników</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AssetSelect;