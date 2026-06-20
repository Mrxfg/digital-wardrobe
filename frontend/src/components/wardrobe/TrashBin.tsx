import { type ClothesItem } from '../../types';
import { THEME } from '../../utils/constants';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  clothes: ClothesItem[];
  setClothes: (clothes: ClothesItem[]) => void;
}

export const TrashBin = ({ isOpen, onClose, clothes, setClothes }: Props) => {
  const deletedItems = clothes.filter(item => item.deletedAt);

  const restoreItem = (itemId: number) => {
    const updatedClothes = clothes.map(item =>
      item.id === itemId
        ? { ...item, deletedAt: undefined }
        : item
    );
    setClothes(updatedClothes);
  };

  const permanentlyDelete = (itemId: number) => {
    const updatedClothes = clothes.filter(item => item.id !== itemId);
    setClothes(updatedClothes);
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.6)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 16,
    }}>
      <div style={{
        background: THEME.bg,
        borderRadius: 24,
        width: '100%',
        maxWidth: 500,
        maxHeight: '80vh',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <div style={{
          padding: 20,
          borderBottom: `1px solid ${THEME.secondary}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <h3 style={{ margin: 0 }}>🗑️ Корзина</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 24, cursor: 'pointer' }}>
            ✕
          </button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: 20 }}>
          {deletedItems.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, opacity: 0.5 }}>
              🗑️ Корзина пуста
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {deletedItems.map(item => {
                const daysLeft = 14 - Math.floor((Date.now() - new Date(item.deletedAt!).getTime()) / (1000 * 60 * 60 * 24));
                return (
                  <div
                    key={item.id}
                    style={{
                      background: THEME.card,
                      padding: 12,
                      borderRadius: 12,
                      display: 'flex',
                      gap: 12,
                      alignItems: 'center',
                    }}
                  >
                    <img
                      src={item.img}
                      alt={item.name}
                      style={{
                        width: 60,
                        height: 60,
                        objectFit: 'cover',
                        borderRadius: 8,
                      }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600 }}>{item.name}</div>
                      <div style={{ fontSize: 11, opacity: 0.6 }}>
                        Удалится через {daysLeft} дней
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button
                        onClick={() => restoreItem(item.id)}
                        style={{
                          padding: '6px 12px',
                          background: THEME.secondary,
                          border: 'none',
                          borderRadius: 8,
                          cursor: 'pointer',
                          fontSize: 12,
                        }}
                      >
                        Восстановить
                      </button>
                      <button
                        onClick={() => permanentlyDelete(item.id)}
                        style={{
                          padding: '6px 12px',
                          background: '#E57373',
                          color: 'white',
                          border: 'none',
                          borderRadius: 8,
                          cursor: 'pointer',
                          fontSize: 12,
                        }}
                      >
                        Удалить
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};