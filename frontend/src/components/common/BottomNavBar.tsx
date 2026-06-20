export const BottomNavBar = ({ currentScreen, onScreenChange }: any) => {
  const tabs = [
    { id: 'wardrobe', label: 'Гардероб', icon: '👕' },
    { id: 'constructor', label: 'Образы', icon: '✨' },
    { id: 'calendar', label: 'Календарь', icon: '📅' },
  ];

  return (
    <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#FFFDF9', borderTop: '1px solid #E0DCD5', display: 'flex', padding: '10px 0 20px' }}>
      {tabs.map(tab => (
        <button key={tab.id} onClick={() => onScreenChange(tab.id)} style={{ flex: 1, background: 'none', border: 'none', cursor: 'pointer', opacity: currentScreen === tab.id ? 1 : 0.5 }}>
          <span style={{ fontSize: 24 }}>{tab.icon}</span>
          <div style={{ fontSize: 11 }}>{tab.label}</div>
        </button>
      ))}
    </div>
  );
};
