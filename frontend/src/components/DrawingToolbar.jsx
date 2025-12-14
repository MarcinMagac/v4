// frontend/src/components/DrawingToolbar.jsx
import React from 'react';
import { Pencil, Minus, Trash2, MousePointer2 } from 'lucide-react';

const DrawingToolbar = ({ activeTool, onSelectTool, onClearAll, drawingsCount }) => {
  const tools = [
    { id: null, icon: <MousePointer2 size={18} />, label: 'Cursor' },
    { id: 'trendline', icon: <Pencil size={18} />, label: 'Trend Line' },
    { id: 'horizontal', icon: <Minus size={18} />, label: 'Horz Level' },
  ];

  return (
    <div className="drawing-toolbar" style={{
      position: 'absolute',
      left: '12px',
      top: '60px',
      zIndex: 20,
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      background: '#1e222d',
      padding: '8px',
      borderRadius: '6px',
      border: '1px solid #2b3139',
      boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
    }}>
      {tools.map(tool => (
        <button
          key={tool.id || 'cursor'}
          onClick={() => onSelectTool(tool.id)}
          title={tool.label}
          style={{
            background: activeTool === tool.id ? '#2962ff' : 'transparent',
            color: activeTool === tool.id ? '#fff' : '#848e9c',
            border: 'none',
            borderRadius: '4px',
            padding: '6px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s'
          }}
        >
          {tool.icon}
        </button>
      ))}

      <div style={{ height: '1px', background: '#2b3139', margin: '4px 0' }} />

      <button
        onClick={onClearAll}
        disabled={drawingsCount === 0}
        title="Clear All Drawings"
        style={{
          background: 'transparent',
          color: drawingsCount > 0 ? '#ef5350' : '#444',
          border: 'none',
          borderRadius: '4px',
          padding: '6px',
          cursor: drawingsCount > 0 ? 'pointer' : 'not-allowed',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <Trash2 size={18} />
      </button>
    </div>
  );
};

export default DrawingToolbar;