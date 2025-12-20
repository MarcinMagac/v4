import React, { useState, useEffect, useRef } from 'react';

const LogConsole = () => {
  const [logs, setLogs] = useState([]);
  const [isMinimized, setIsMinimized] = useState(false); // Domyślnie otwarte
  const bottomRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      fetch('http://127.0.0.1:8000/api/logs')
        .then(res => res.json())
        .then(data => {
          if (data.logs && data.logs.length > 0) {
            setLogs(prev => [...prev, ...data.logs]);
          }
        })
        .catch(() => {}); // Cicho ignoruj błędy sieci
    }, 500);

    return () => clearInterval(interval);
  }, []);

  // Przewijaj na dół tylko gdy konsola jest otwarta
  useEffect(() => {
    if (!isMinimized) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, isMinimized]);

  if (logs.length === 0) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      width: '100%',
      // Zmiana wysokości w zależności od stanu
      height: isMinimized ? '35px' : '150px',
      backgroundColor: 'rgba(0, 0, 0, 0.9)',
      color: '#00ff00',
      fontFamily: 'monospace',
      fontSize: '12px',
      zIndex: 9999,
      borderTop: '2px solid #333',
      backdropFilter: 'blur(3px)',
      transition: 'height 0.3s ease-in-out', // Płynna animacja
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* NAGŁÓWEK KONSOLI */}
      <div style={{
        borderBottom: isMinimized ? 'none' : '1px solid #444',
        padding: '5px 10px',
        fontWeight: 'bold',
        color: '#fff',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        cursor: 'pointer',
        backgroundColor: '#1a1a1a'
      }}
      onClick={() => setIsMinimized(!isMinimized)} // Klik w pasek też minimalizuje
      >
        <span>SYSTEM LOGS {isMinimized ? '(Hidden)' : '(Live)'}</span>

        <div style={{ display: 'flex', gap: '15px' }}>
            <span
                style={{cursor: 'pointer', color: '#888'}}
                onClick={(e) => { e.stopPropagation(); setLogs([]); }}
            >
                [Clear]
            </span>
            <span style={{cursor: 'pointer', color: '#fff'}}>
                {isMinimized ? '[\u25B2] Maximize' : '[\u25BC] Minimize'}
            </span>
        </div>
      </div>

      {/* TREŚĆ KONSOLI (Ukryta gdy zminimalizowana) */}
      {!isMinimized && (
        <div style={{
            overflowY: 'auto',
            padding: '10px',
            flex: 1
        }}>
          {logs.map((log, index) => (
            <div key={index} style={{ marginBottom: '2px' }}>
              <span style={{ opacity: 0.5, marginRight: '8px' }}>{'>'}</span>
              {log}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
};

export default LogConsole;