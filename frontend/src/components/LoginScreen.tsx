import { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100dvh',
    backgroundColor: '#FDFBF7',
    padding: '24px',
    gap: '24px',
  },
  title: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#373635',
    textAlign: 'center' as const,
    lineHeight: '1.2',
  },
  subtitle: {
    fontSize: '16px',
    color: '#6B6A69',
    textAlign: 'center' as const,
    maxWidth: '320px',
    lineHeight: '1.5',
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '3px solid #E6E5E3',
    borderTop: '3px solid #373635',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  },
  errorBox: {
    backgroundColor: '#FEF2F2',
    border: '1px solid #FECACA',
    borderRadius: '12px',
    padding: '16px',
    color: '#DC2626',
    fontSize: '14px',
    maxWidth: '320px',
    textAlign: 'center' as const,
  },
  retryButton: {
    backgroundColor: '#373635',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '12px',
    padding: '12px 32px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    width: '100%',
    maxWidth: '320px',
  },
  mockButton: {
    backgroundColor: '#8B8A89',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '12px',
    padding: '10px 24px',
    fontSize: '13px',
    cursor: 'pointer',
    marginTop: '8px',
  },
};

// Inject spinner keyframes
const styleSheet = document.createElement('style');
styleSheet.textContent = `@keyframes spin { to { transform: rotate(360deg); } }`;
document.head.appendChild(styleSheet);

export default function LoginScreen() {
  const { login, isLoading, error, clearError, isTelegram } = useAuth();

  const handleTelegramLogin = () => {
    const webapp = (window as any).Telegram?.WebApp;
    if (webapp?.initData) {
      login(webapp.initData);
    }
  };

  // Dev/test: login without Telegram (browser preview)
  const handleDevLogin = async () => {
    try {
      // Try to open Telegram login popup or use mock data
      const mockInitData = JSON.stringify({
        id: 123456789,
        first_name: 'Test',
        username: 'test_user',
        auth_date: Math.floor(Date.now() / 1000),
        hash: 'test_hash',
      });
      // This will fail on backend since hash is fake, but shows the flow
      await login('user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22Test%22%2C%22username%22%3A%22test_user%22%7D&auth_date=0&hash=fake');
    } catch {
      // Expected to fail outside Telegram — handled by error state
    }
  };

  if (isLoading) {
    return (
      <div style={styles.container}>
        <div style={styles.spinner} />
        <div style={styles.title}>Digital Wardrobe</div>
        <div style={styles.subtitle}>Выполняется вход...</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.title}>Digital Wardrobe</div>
      <div style={styles.subtitle}>
        Ваш персональный цифровой гардероб в Telegram
      </div>

      {error && (
        <div style={styles.errorBox}>
          <div style={{ fontWeight: '600', marginBottom: '4px' }}>Ошибка входа</div>
          <div>{error}</div>
        </div>
      )}

      {isTelegram ? (
        <button onClick={handleTelegramLogin} style={styles.retryButton}>
          Войти через Telegram
        </button>
      ) : (
        <>
          <button onClick={handleDevLogin} style={styles.retryButton}>
            Войти
          </button>
          <button onClick={handleDevLogin} style={styles.mockButton}>
            Режим разработки (тестовый вход)
          </button>
        </>
      )}
    </div>
  );
}
