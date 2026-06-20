import { useState } from 'react';
import { useSubscription } from '../../hooks/useSubscription';
import { SubscriptionModal } from '../SubscriptionModal';

interface ClothesItem {
  id: number;
  name: string;
  category: string;
  season: string;
  img: string;
  deletedAt?: string | null;
  createdAt: string;
}

interface Props {
  clothes: ClothesItem[];
  setClothes: (clothes: ClothesItem[]) => void;
  history: any[];
}

const SEASONS = [
  { id: 'Зима', name: 'Зима', color: '#6BB5E0' },
  { id: 'Весна', name: 'Весна', color: '#E8A87C' },
  { id: 'Лето', name: 'Лето', color: '#F3D572' },
  { id: 'Осень', name: 'Осень', color: '#D4956A' },
  { id: 'Демисезон', name: 'Демисезон', color: '#A8C8A0' },
];

const getTelegramTheme = () => ({
  bg: '#0D0C0F', card: '#1A1A1E', primary: '#C4A47A', primaryText: '#0D0C0F',
  secondary: '#2A2A2E', text: '#FFFFFF', textSecondary: '#A0A0A0',
  gradient: 'linear-gradient(135deg, #C4A47A 0%, #E8D5B5 100%)',
});

export const WardrobeGrid = ({ clothes, setClothes, history }: Props) => {
  const [showAdd, setShowAdd] = useState(false);
  const [newName, setNewName] = useState('');
  const [newCategory, setNewCategory] = useState('top');
  const [newSeason, setNewSeason] = useState('Лето');
  const [newImage, setNewImage] = useState<string | null>(null);
  const [filterSeason, setFilterSeason] = useState<string | null>(null);
  const theme = getTelegramTheme();

  const { isPremium, showPayModal, setShowPayModal, getRemainingFreeSlots, activatePremium, canAddItem, freeLimit } = useSubscription();

  const getWornCount = (itemId: number) => history.filter(h => h.itemId === itemId).length;

  const handleImageSelected = (imageDataUrl: string) => {
    setNewImage(imageDataUrl);
  };

  const saveItem = () => {
    if (!newName) { alert('Введите название'); return; }
    if (!newImage) { alert('Добавьте фото'); return; }
    
    const currentCount = clothes.filter(c => !c.deletedAt).length;
    if (!canAddItem(currentCount)) return;
    
    const newItem = {
      id: Date.now(),
      name: newName,
      category: newCategory,
      season: newSeason,
      img: newImage,
      createdAt: new Date().toISOString(),
    };
    setClothes([newItem, ...clothes]);
    setShowAdd(false);
    setNewName('');
    setNewImage(null);
    alert('Вещь добавлена!');
  };

  const deleteItem = (id: number) => {
    setClothes(clothes.map(c => c.id === id ? { ...c, deletedAt: new Date().toISOString() } : c));
  };

  let visibleClothes = clothes.filter(i => !i.deletedAt);
  if (filterSeason) visibleClothes = visibleClothes.filter(c => c.season === filterSeason);

  return (
    <div style={{ padding: 20, paddingBottom: 100 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, background: theme.gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Гардероб</h1>
        <p style={{ color: theme.textSecondary }}>{visibleClothes.length} вещей</p>
      </div>

      {/* Filter by seasons */}
      <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 8, marginBottom: 24 }}>
        <button onClick={() => setFilterSeason(null)} style={{ padding: '8px 16px', borderRadius: 20, background: !filterSeason ? theme.primary : theme.secondary, border: 'none', color: !filterSeason ? theme.primaryText : theme.textSecondary }}>Все сезоны</button>
        {SEASONS.map(s => (
          <button key={s.id} onClick={() => setFilterSeason(s.id)} style={{ padding: '8px 16px', borderRadius: 20, background: filterSeason === s.id ? s.color : theme.secondary, border: 'none', color: filterSeason === s.id ? '#0D0C0F' : theme.textSecondary }}>{s.name}</button>
        ))}
      </div>

      {!isPremium && visibleClothes.length > 0 && (
        <div style={{
          background: theme.secondary,
          borderRadius: 16,
          padding: '10px 16px',
          marginBottom: 20,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 10,
        }}>
          <div style={{ fontSize: 13, color: theme.text }}>
            📦 Бесплатно: {getRemainingFreeSlots(visibleClothes.length)} из {freeLimit} мест осталось
          </div>
          <button 
            onClick={() => setShowPayModal(true)} 
            style={{
              background: theme.gradient,
              border: 'none',
              borderRadius: 20,
              padding: '6px 16px',
              fontSize: 12,
              fontWeight: 600,
              cursor: 'pointer',
              color: theme.primaryText,
            }}
          >
            Расширить
          </button>
        </div>
      )}

      {visibleClothes.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 60, background: theme.card, borderRadius: 24 }}>
          <p style={{ color: theme.textSecondary }}>Добавьте первую вещь</p>
          <button onClick={() => setShowAdd(true)} style={{ marginTop: 16, padding: '12px 24px', background: theme.gradient, border: 'none', borderRadius: 30, cursor: 'pointer' }}>+ Добавить</button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          {visibleClothes.map(item => (
            <div key={item.id} style={{ background: theme.card, borderRadius: 16, padding: 12, position: 'relative' }}>
              <img src={item.img} style={{ width: '100%', aspectRatio: '1/1', objectFit: 'cover', borderRadius: 12, marginBottom: 8 }} alt="" />
              <div style={{ fontWeight: 500 }}>{item.name}</div>
              <div style={{ fontSize: 11, color: theme.textSecondary, marginTop: 4 }}>{getWornCount(item.id)} раз</div>
              <button onClick={() => deleteItem(item.id)} style={{ position: 'absolute', top: 8, right: 8, background: 'rgba(0,0,0,0.6)', border: 'none', borderRadius: 20, padding: '4px 8px', color: 'white', cursor: 'pointer' }}>🗑️</button>
            </div>
          ))}
        </div>
      )}

      <button onClick={() => setShowAdd(true)} style={{ position: 'fixed', bottom: 80, right: 20, width: 56, height: 56, borderRadius: 28, background: theme.gradient, border: 'none', fontSize: 28, cursor: 'pointer', boxShadow: '0 4px 12px rgba(0,0,0,0.3)' }}>+</button>
      {showAdd && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.9)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: theme.card, borderRadius: 24, padding: 24, width: '90%', maxWidth: 400 }}>
            <h3 style={{ marginBottom: 20, color: theme.text }}>➕ Новая вещь</h3>
            
            {!newImage ? (
              <input type="file" accept="image/*" onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onloadend = () => handleImageSelected(reader.result as string);
                  reader.readAsDataURL(file);
                }
              }} style={{ marginBottom: 16 }} />
            ) : (
              <div style={{ position: 'relative', marginBottom: 16 }}>
                <img src={newImage} style={{ width: '100%', borderRadius: 12 }} alt="" />
                <button onClick={() => setNewImage(null)} style={{ position: 'absolute', top: 8, right: 8, background: 'rgba(0,0,0,0.6)', border: 'none', borderRadius: 20, padding: '4px 12px', color: 'white', cursor: 'pointer' }}>Заменить</button>
              </div>
            )}
            
            <input placeholder="Название вещи" value={newName} onChange={(e) => setNewName(e.target.value)} style={{ width: '100%', padding: 12, borderRadius: 12, border: `1px solid ${theme.secondary}`, background: theme.bg, color: theme.text, marginBottom: 12 }} />
            
            <select value={newCategory} onChange={(e) => setNewCategory(e.target.value)} style={{ width: '100%', padding: 12, borderRadius: 12, border: `1px solid ${theme.secondary}`, background: theme.bg, color: theme.text, marginBottom: 12 }}>
              <option value="top">Верх</option>
              <option value="bottom">Низ</option>
              <option value="shoes">Обувь</option>
            </select>
            
            <select value={newSeason} onChange={(e) => setNewSeason(e.target.value)} style={{ width: '100%', padding: 12, borderRadius: 12, border: `1px solid ${theme.secondary}`, background: theme.bg, color: theme.text, marginBottom: 20 }}>
              {SEASONS.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            
            <div style={{ display: 'flex', gap: 12 }}>
              <button onClick={saveItem} style={{ flex: 1, padding: 14, background: theme.gradient, border: 'none', borderRadius: 12, cursor: 'pointer', fontWeight: 600 }}>Сохранить</button>
              <button onClick={() => { setShowAdd(false); setNewImage(null); setNewName(''); }} style={{ flex: 1, padding: 14, background: theme.secondary, border: 'none', borderRadius: 12, cursor: 'pointer' }}>Отмена</button>
            </div>
          </div>
        </div>
      )}

      {/* Subscription */}
      <SubscriptionModal
        isOpen={showPayModal}
        onClose={() => setShowPayModal(false)}
        onUpgrade={activatePremium}
        theme={theme}
        freeLimit={freeLimit}
        currentItemsCount={visibleClothes.length}
      />
    </div>
  );
};
