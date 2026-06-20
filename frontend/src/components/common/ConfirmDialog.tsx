interface Props {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmDialog = ({ isOpen, title, message, onConfirm, onCancel }: Props) => {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.6)',
      zIndex: 2000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 16,
    }}>
      <div style={{
        background: 'white',
        borderRadius: 20,
        padding: 24,
        maxWidth: 300,
        width: '100%',
      }}>
        <h4 style={{ marginBottom: 8, color: '#655446' }}>{title}</h4>
        <p style={{ marginBottom: 20, color: '#8C7662', fontSize: 14 }}>{message}</p>
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            onClick={onCancel}
            style={{ flex: 1, padding: 10, background: '#F4EFE6', border: 'none', borderRadius: 10, cursor: 'pointer' }}
          >
            Отмена
          </button>
          <button
            onClick={onConfirm}
            style={{ flex: 1, padding: 10, background: '#8C7662', color: 'white', border: 'none', borderRadius: 10, cursor: 'pointer' }}
          >
            Да
          </button>
        </div>
      </div>
    </div>
  );
};