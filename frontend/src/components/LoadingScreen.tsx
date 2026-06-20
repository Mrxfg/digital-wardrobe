import { useEffect, useState } from 'react';

const LoadingScreen = () => {
  const [progress, setProgress] = useState(0);
  const theme = {
    bg: '#FFFFF0',
    primary: '#442F29',
    text: '#442F29',
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(timer);
          return 100;
        }
        return prev + 10;
      });
    }, 50);

    return () => clearInterval(timer);
  }, []);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: theme.bg,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
    }}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
      }}>
        <img 
          src="/ICON.png" 
          alt="Wardrobe" 
          style={{ 
            width: 80, 
            height: 80, 
            marginBottom: 24,
          }} 
        />
        <p style={{
          fontFamily: 'Inter, sans-serif',
          fontSize: 14,
          color: '#8B7355',
        }}>Загружаем гардероб...</p>

        <div style={{
          width: 200,
          height: 2,
          background: '#E8E0D5',
          borderRadius: 2,
          marginTop: 32,
          overflow: 'hidden',
        }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            background: theme.primary,
            transition: 'width 0.1s ease',
          }} />
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;
