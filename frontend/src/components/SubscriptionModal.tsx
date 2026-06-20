interface Props {
  isOpen: boolean;
  onClose: () => void;
  onUpgrade: () => void;
  theme: any;
  freeLimit: number;
  currentItemsCount: number;
}

export const SubscriptionModal = ({ isOpen, onClose, onUpgrade, theme, freeLimit, currentItemsCount }: Props) => {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.9)',
      zIndex: 2000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 20,
    }}>
      <div style={{
        background: theme.card,
        borderRadius: 28,
        padding: 24,
        width: '100%',
        maxWidth: 380,
        textAlign: 'center',
      }}>
        <h2 style={{ margin: 0, color: theme.text }}>Premium доступ</h2>
        <p style={{ color: theme.textSecondary, marginTop: 8 }}>
          Вы добавили {currentItemsCount} из {freeLimit} бесплатных вещей
        </p>

        <div style={{
          background: theme.bg,
          borderRadius: 20,
          padding: 20,
          margin: '20px 0',
        }}>
          <div style={{ fontSize: 36, fontWeight: 700, color: theme.primary }}>199 ₽</div>
          <div style={{ fontSize: 12, color: theme.textSecondary }}>/месяц</div>
        </div>

        <div style={{ marginBottom: 20, textAlign: 'left' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
            <span style={{ color: theme.text }}>Безлимит вещей</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
             <span style={{ color: theme.text }}>Все капсулы (8-3 и 10-5)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
             <span style={{ color: theme.text }}>AI обработка фото</span>
          </div>
        </div>

        <button
          onClick={onUpgrade}
          style={{
            width: '100%',
            padding: 16,
            background: theme.gradient,
            border: 'none',
            borderRadius: 20,
            fontSize: 18,
            fontWeight: 700,
            color: theme.primaryText,
            cursor: 'pointer',
            marginBottom: 12,
          }}
        >
          Получить Premium
        </button>

        <button
          onClick={onClose}
          style={{
            width: '100%',
            padding: 12,
            background: 'none',
            border: `1px solid ${theme.secondary}`,
            borderRadius: 20,
            fontSize: 14,
            color: theme.textSecondary,
            cursor: 'pointer',
          }}
        >
          Возможно, позже
        </button>
      </div>
    </div>
  );
};
