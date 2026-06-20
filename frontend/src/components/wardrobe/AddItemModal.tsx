import { useState } from 'react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSave: (item: any) => void;
}

export const AddItemModal = ({ isOpen, onClose, onSave }: Props) => {
  const [name, setName] = useState('');
  const [category, setCategory] = useState('top');
  const [season, setSeason] = useState('Демисезон');

  if (!isOpen) return null;

  const handleSave = () => {
    const newItem = {
      id: Date.now(),
      name: name || 'Новая вещь',
      category,
      season,
      img: 'https://via.placeholder.com/150?text=Новая+вещь',
      createdAt: new Date().toISOString(),
    };
    onSave(newItem);
    onClose();
    setName('');
  };

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
        background: '#FDFBF7',
        borderRadius: 24,
        width: '100%',
        maxWidth: 400,
        padding: 20,
      }}>
        <h3 style={{ margin: '0 0 16px 0' }}>➕ Добавить вещь</h3>
        
        <input
          type="text"
          placeholder="Название вещи"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{
            width: '100%',
            padding: 12,
            borderRadius: 10,
            border: '1px solid #E0DCD5',
            marginBottom: 12,
            boxSizing: 'border-box',
          }}
        />
        
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={{
            width: '100%',
            padding: 12,
            borderRadius: 10,
            border: '1px solid #E0DCD5',
            marginBottom: 12,
          }}
        >
          <option value="top">Верх</option>
          <option value="bottom">Низ</option>
          <option value="shoes">Обувь</option>
          <option value="accessory">Аксессуар</option>
        </select>
        
        <select
          value={season}
          onChange={(e) => setSeason(e.target.value)}
          style={{
            width: '100%',
            padding: 12,
            borderRadius: 10,
            border: '1px solid #E0DCD5',
            marginBottom: 20,
          }}
        >
          <option value="Зима">Зима</option>
          <option value="Лето">Лето</option>
          <option value="Осень">Осень</option>
          <option value="Весна">Весна</option>
          <option value="Демисезон">Демисезон</option>
        </select>
        
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            onClick={onClose}
            style={{ flex: 1, padding: 12, background: '#F4EFE6', border: 'none', borderRadius: 10, cursor: 'pointer' }}
          >
            Отмена
          </button>
          <button
            onClick={handleSave}
            style={{ flex: 1, padding: 12, background: '#8C7662', color: 'white', border: 'none', borderRadius: 10, cursor: 'pointer' }}
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
  );
};
