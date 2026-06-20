import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

const styles = {
  button: {
    backgroundColor: 'transparent',
    border: '1px solid #E6E5E3',
    borderRadius: '10px',
    padding: '8px 16px',
    fontSize: '13px',
    color: '#6B6A69',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    transition: 'all 0.2s',
  },
  buttonHover: {
    border: '1px solid #E57373',
    color: '#E57373',
    backgroundColor: '#FEF2F2',
  },
  confirmOverlay: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '24px',
  },
  confirmDialog: {
    backgroundColor: '#FFFFFF',
    borderRadius: '16px',
    padding: '24px',
    maxWidth: '320px',
    width: '100%',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
  },
  confirmTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#373635',
    textAlign: 'center' as const,
  },
  confirmText: {
    fontSize: '14px',
    color: '#6B6A69',
    textAlign: 'center' as const,
    lineHeight: '1.4',
  },
  confirmButtons: {
    display: 'flex',
    gap: '12px',
    marginTop: '8px',
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#F4EFE6',
    border: 'none',
    borderRadius: '12px',
    padding: '12px',
    fontSize: '15px',
    fontWeight: '500',
    color: '#373635',
    cursor: 'pointer',
  },
  logoutButton: {
    flex: 1,
    backgroundColor: '#E57373',
    border: 'none',
    borderRadius: '12px',
    padding: '12px',
    fontSize: '15px',
    fontWeight: '500',
    color: '#FFFFFF',
    cursor: 'pointer',
  },
};

export default function LogoutButton() {
  const { logout, user } = useAuth();
  const [showConfirm, setShowConfirm] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const handleLogout = () => {
    setShowConfirm(false);
    logout();
  };

  return (
    <>
      <button
        style={isHovered ? { ...styles.button, ...styles.buttonHover } : styles.button}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={() => setShowConfirm(true)}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
        {user?.first_name || 'Выйти'}
      </button>

      {showConfirm && (
        <div style={styles.confirmOverlay} onClick={() => setShowConfirm(false)}>
          <div style={styles.confirmDialog} onClick={(e) => e.stopPropagation()}>
            <div style={styles.confirmTitle}>Выйти из аккаунта?</div>
            <div style={styles.confirmText}>
              Вам потребуется повторная авторизация через Telegram
            </div>
            <div style={styles.confirmButtons}>
              <button style={styles.cancelButton} onClick={() => setShowConfirm(false)}>
                Отмена
              </button>
              <button style={styles.logoutButton} onClick={handleLogout}>
                Выйти
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
