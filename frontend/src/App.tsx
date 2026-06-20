import { useState, useEffect, useRef } from 'react';
import { useLocalStorage } from './hooks/useLocalStorage';
import { AuthProvider, useAuth } from './hooks/useAuth';
import LoginScreen from './components/LoginScreen';
import LogoutButton from './components/LogoutButton';

interface WardrobeItem {
  id: number;
  name: string;
  category: string;
  season: string;
  color: string;
  material: string;
  img: string;
  createdAt: string;
  deletedAt: string | null;
}

const getTheme = () => {
  return {
    bg: '#E6E5E3',
    card: '#FFFFFF',
    primary: '#373635',
    primaryText: '#FFFFFF',
    secondary: '#D4D3D1',
    text: '#373635',
    textSecondary: '#6B6A69',
    accent: '#8B8A89',
    destructive: '#E57373',
    success: '#4CAF50',
    gradient: 'linear-gradient(135deg, #373635 0%, #5A5958 100%)',
  };
};

const СЕЗОНЫ = [
  { id: 'winter', name: 'Зима', color: '#6BB5E0' },
  { id: 'spring', name: 'Весна', color: '#E8A87C' },
  { id: 'summer', name: 'Лето', color: '#F3D572' },
  { id: 'autumn', name: 'Осень', color: '#D4956A' },
  { id: 'demiseason', name: 'Демисезон', color: '#A8C8A0' },
];

const ЦВЕТА = [
  { id: 'white', name: 'Белый', hex: '#FFFFFF' },
  { id: 'black', name: 'Черный', hex: '#000000' },
  { id: 'beige', name: 'Бежевый', hex: '#D4C5B9' },
  { id: 'brown', name: 'Коричневый', hex: '#8B6F4E' },
  { id: 'navy', name: 'Темно-синий', hex: '#2C3E50' },
  { id: 'grey', name: 'Серый', hex: '#95A5A6' },
  { id: 'red', name: 'Красный', hex: '#E57373' },
  { id: 'blue', name: 'Синий', hex: '#6BB5E0' },
  { id: 'green', name: 'Зеленый', hex: '#81C784' },
  { id: 'pink', name: 'Розовый', hex: '#F8B4B4' },
  { id: 'purple', name: 'Фиолетовый', hex: '#C4A4D4' },
  { id: 'orange', name: 'Оранжевый', hex: '#F39C12' },
  { id: 'yellow', name: 'Желтый', hex: '#F1C40F' },
];

const МАТЕРИАЛЫ = [
  { id: "cotton", name: "Хлопок" },
  { id: "synthetic", name: "Синтетика" },
  { id: "mixed", name: "Смешанная" },
  { id: "viscose", name: "Вискоза" },
  { id: "linen", name: "Лен" },
  { id: "wool", name: "Шерсть" },
  { id: "silk", name: "Шелк" },
];

const КАТЕГОРИИ = [
  { id: "all", name: "Все" },
  { id: "top", name: "Верх" },
  { id: "bottom", name: "Низ" },
  { id: "shoes", name: "Обувь" },
  { id: "accessory", name: "Аксессуары" },
];

const useMediaQuery = (query: string) => {
  const [matches, setMatches] = useState(false);
  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) setMatches(media.matches);
    const listener = (e: MediaQueryListEvent) => setMatches(e.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [matches, query]);
  return matches;
};

const useTelegram = () => {
  const [tg, setTg] = useState<any>(null);
  const [initData, setInitData] = useState<string>('');
  const [isTelegram, setIsTelegram] = useState<boolean>(true); // по умолчанию считаем, что в ТГ
  
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Приводим к any, чтобы TypeScript не ругался на отсутствие полей
      const webapp = (window as any).Telegram?.WebApp;
      
      // Проверяем, есть ли SDK и не пустая ли initData
      if (webapp && webapp.initData) {
        webapp.ready();
        webapp.expand();
        webapp.enableClosingConfirmation();
        setTg(webapp);
        setInitData(webapp.initData);
        setIsTelegram(true);
      } else {
        setIsTelegram(false); // Мы в обычном браузере
      }
    }
  }, []);
  
  const haptic = (style: 'light' | 'medium' | 'heavy' = 'medium') => {
    if (tg?.HapticFeedback) {
      tg.HapticFeedback.impactOccurred(style);
    }
  };
  
  return { tg, initData, isTelegram, haptic };
};

const PhotoPicker = ({ onImageSelected }: any) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  return (
    <>
      <div 
        onClick={() => fileInputRef.current?.click()}
        style={drawerStyles.photoPickerZone}
      >
        <div style={drawerStyles.pickerCircle}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#151414" strokeWidth="1.5" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </div>
        <span style={{ fontSize: '15px', color: '#151414', fontWeight: '600' }}>Выбрать фото</span>
        <span style={{ fontSize: '12px', color: '#6B6A69' }}>Нажмите, чтобы выбрать файл</span>
      </div>
      <input 
        ref={fileInputRef}
        type="file" 
        accept="image/*" 
        style={{ display: 'none' }} 
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
              onImageSelected(reader.result as string);
            };
            reader.readAsDataURL(file);
          }
        }}
      />
    </>
  );
};

const BottomNavBar = ({ currentScreen, onScreenChange }: { currentScreen: string; onScreenChange: (screen: any) => void }) => {
  const tabs = [
    { id: 'home', label: 'ГС' },
    { id: 'profile', label: 'ЛК' },
  ];

  return (
    <div style={navStyles.navBarContainer}>
      <div style={navStyles.navBar}>
        {tabs.map(tab => {
          const isActive = currentScreen === tab.id;
          return (
            <button 
              key={tab.id} 
              onClick={() => {
                onScreenChange(tab.id);
                if (typeof window !== 'undefined') {
                  const searchInput = document.querySelector('input[type="text"]');
                  if (searchInput) (searchInput as HTMLInputElement).value = '';
                }
              }} 
              style={navStyles.navButton}
            >
              {tab.id === 'home' && (
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9 22 9 12 15 12 15 22"/>
                </svg>
              )}
              {tab.id === 'profile' && (
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              )}
              {isActive && <div style={navStyles.activeIndicator} />}
            </button>
          );
        })}
      </div>
    </div>
  );
};

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();
  const { isTelegram, haptic } = useTelegram();

  if (isLoading) {
    return <LoginScreen />;
  }

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  return <AppMain isTelegram={isTelegram} haptic={haptic} />;
}

function AppMain({ isTelegram, haptic }: { isTelegram: boolean; haptic: (style?: 'light' | 'medium' | 'heavy') => void }) {
  const [currentScreen, setCurrentScreen] = useState<'home' | 'profile' | 'cart'>('home');
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedItemForView, setSelectedItemForView] = useState<any | null>(null);
  const [newName, setNewName] = useState('');
  const [newCategory, setNewCategory] = useState('');
  const [newSeason, setNewSeason] = useState('');
  const [newColor, setNewColor] = useState('');
  const [newMaterial, setNewMaterial] = useState('');
  const [newImage, setNewImage] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [drawerError, setDrawerError] = useState<string | null>(null);
  const [clothes, setClothes] = useLocalStorage<any[]>('clothes', []);
  const [outfits, setOutfits] = useLocalStorage<any[]>('outfits', []); 
  const [capsules, setCapsules] = useLocalStorage<any[]>('capsules', []); 
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [selectedItems, setSelectedItems] = useState<any[]>([]);
  const [isOutfitCreatorOpen, setIsOutfitCreatorOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [outfitName, setOutfitName] = useState('');

  // Функция для генерации дней текущего месяца
  const getCalendarDays = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();

    const firstDayOfMonth = new Date(year, month, 1);
    let startDayOfWeek = firstDayOfMonth.getDay();
    startDayOfWeek = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1;

    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const days = [];

    for (let i = 0; i < startDayOfWeek; i++) {
      days.push({ day: null, isToday: false });
    }

    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
      const isToday =
        day === today.getDate() &&
        month === today.getMonth() &&
        year === today.getFullYear();
      
      days.push({ day, isToday });
    }
    return days;
  };

  const calendarDays = getCalendarDays();
  
  const toggleItemSelection = (item: any) => {
    if (selectedItems.find((i: any) => i.id === item.id)) {
      setSelectedItems(selectedItems.filter((i: any) => i.id !== item.id));
    } else {
      setSelectedItems([...selectedItems, item]);
      haptic('light');
    }
  };

  useEffect(() => {
    const styleTag = document.createElement('style');
    styleTag.textContent = `
      @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500&family=Inter:wght@400;500;600&display=swap');
      
      body, button, input, select, textarea, span, div {
        font-family: 'Inter', sans-serif !important;
      }
      
      .fancy-serif {
        font-family: 'Playfair Display', serif !important;
        font-style: normal !important;
        font-weight: 400 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase;
      }

      h1.fancy-serif {
        letter-spacing: 1.5px !important;
      }

      [style*="dayNumber"], [style*="calendarDaysHeader"] span {
        font-family: 'Inter', sans-serif !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        font-weight: 500 !important;
      }
    `;
    document.head.appendChild(styleTag);

    document.body.style.backgroundColor = '#edecea';
    document.body.style.color = '#151414';
    if (document.documentElement) {
      document.documentElement.style.backgroundColor = '#edecea';
    }

    return () => {
      if (document.head.contains(styleTag)) {
        document.head.removeChild(styleTag);
      }
    };
  }, []);



  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#edecea', position: 'relative', width: '100%', boxSizing: 'border-box' }}>
      
      {/* СЦЕНАРИЙ 3: Заглушка для браузера خارج Телеграма */}
      {!isTelegram && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          padding: '24px',
          textAlign: 'center',
          backgroundColor: '#edecea',
          color: '#151414',
          fontFamily: 'Inter, sans-serif'
        }}>
          <span style={{ fontSize: '48px', marginBottom: '16px' }}></span>
          <h2 className="fancy-serif" style={{ fontSize: '20px', margin: '0 0 12px 0', letterSpacing: '1px' }}>Доступ ограничен</h2>
          <p style={{ fontSize: '14px', color: '#6B6A69', margin: 0, maxWidth: '280px', lineHeight: '1.5' }}>
            Пожалуйста, откройте это приложение внутри Telegram-бота «Цифровой гардероб».
          </p>
        </div>
      )}

      {currentScreen === 'home' && (
            <div style={pageStyle}>
              <div style={headerStyles.headerContainer}>
                <div style={{ width: '42px', height: '42px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <img 
                    src="/Icon.png" 
                    alt="VS Logo" 
                    style={{ width: '60px', height: '60px', objectFit: 'contain' }} 
                  />
                </div>
                <h1 style={headerStyles.headerTitle} className="fancy-serif">ГЛАВНАЯ</h1>
              </div>

              <div style={outfitStyles.sectionContainer}>
                <h2 style={outfitStyles.sectionTitle} className="fancy-serif">Аутфит сегодня</h2>
                <div style={outfitStyles.mainRow}>
                  <div style={outfitStyles.outfitCard}>
                    {outfits.length > 0 ? (
                      (() => {
                        const latestOutfit = outfits[outfits.length - 1];
                        return (
                          <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                            <span style={outfitStyles.outfitName}>{latestOutfit.name}</span>
                            <div style={outfitStyles.itemsGrid}>
                              {latestOutfit.items.slice(0, 4).map((item: any, idx: number) => (
                                <img key={item.id || idx} src={item.img} alt="" style={outfitStyles.gridImage} />
                              ))}
                            </div>
                          </div>
                        );
                      })()
                    ) : (
                      <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
                        <span style={outfitStyles.outfitName}>Название</span>
                        <div style={outfitStyles.emptyGrid}>
                          <span style={{ fontSize: '11px', color: '#8B8A89', textAlign: 'center', padding: '0 4px' }}>
                            Нет образов
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  <div style={widgetStyles.weatherCard}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <div style={widgetStyles.weatherCity}>Санкт-Петербург</div>
                        <div style={widgetStyles.weatherTemp}>+17°</div>
                      </div>
                      <span style={{ fontSize: '11px', fontWeight: '500' }}>Ясно</span>
                    </div>
                    <div style={widgetStyles.hourlyRow}>
                      <div style={widgetStyles.hourItem}><div>4:00</div><div style={{ fontWeight: '600' }}>+18°</div></div>
                      <div style={widgetStyles.hourItem}><div>5:00</div><div style={{ fontWeight: '600' }}>+19°</div></div>
                      <div style={widgetStyles.hourItem}><div>6:00</div><div style={{ fontWeight: '600' }}>+20°</div></div>
                      <div style={widgetStyles.hourItem}><div>7:00</div><div style={{ fontWeight: '600' }}>+20°</div></div>
                    </div>
                  </div>

                  <div style={widgetStyles.calendarCard}>
                    <div style={widgetStyles.calendarDaysHeader}>
                      <span>MON</span><span>TUE</span><span>WED</span><span>THU</span><span>FRI</span><span>SAT</span><span>SUN</span>
                    </div>
                    <div style={widgetStyles.calendarGrid}>
                      {calendarDays.map((item, idx) => (
                        <div 
                          key={idx} 
                          style={{
                            ...widgetStyles.dayCell,
                            backgroundColor: item.isToday ? '#151414' : 'transparent',
                            borderRadius: item.isToday ? '50%' : '0',
                          }}
                        >
                          <span 
                            style={{
                              ...widgetStyles.dayNumber,
                              color: item.isToday ? '#FFFFFF' : item.day ? '#151414' : 'transparent'
                            }}
                          >
                            {item.day}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div style={homeStyles.buttonContainer}>
                <button 
                  style={homeStyles.addBtn} 
                  onClick={() => {
                    setIsDrawerOpen(true);
                    haptic('light');
                  }}
                >
                  <div style={homeStyles.plusCircle}>
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#151414" strokeWidth="1" strokeLinecap="round">
                      <line x1="12" y1="4" x2="12" y2="20"></line>
                      <line x1="4" y1="12" x2="20" y2="12"></line>
                    </svg>
                  </div>
                  <span style={homeStyles.btnText} className="fancy-serif">ДОБАВИТЬ ВЕЩЬ</span>
                </button>
              </div>
            </div>
          )}

          {currentScreen === 'profile' && (
            <div style={pageStyle}>
              <div style={headerStyles.headerContainer}>
                <div style={{ width: '42px', height: '42px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <img
                    src="/Icon.png"
                    alt="VS Logo"
                    style={{ width: '60px', height: '60px', objectFit: 'contain' }}
                  />
                </div>
                <h1 style={{ ...headerStyles.headerTitle, marginLeft: '40px' }} className="fancy-serif">ГАРДЕРОБ</h1>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <LogoutButton />
                  <button
                    onClick={() => {
                      setCurrentScreen('cart');
                      haptic('light');
                    }}
                    style={headerStyles.searchBtn}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6" />
                    </svg>
                  </button>
                </div>
              </div>

              <ProfileGallery 
                clothes={clothes} 
                setClothes={setClothes}
                outfits={outfits} 
                setOutfits={setOutfits}
                capsules={capsules}
                setCapsules={setCapsules}
                searchQuery={searchQuery}
                setIsSearchOpen={setIsSearchOpen}
                haptic={haptic}
                setIsOutfitCreatorOpen={setIsOutfitCreatorOpen}
                setIsDrawerOpen={setIsDrawerOpen}
                onItemClick={setSelectedItemForView} 
              />
            </div>
          )}

          {currentScreen === 'cart' && (
            <div style={pageStyle}>
              <div style={headerStyles.headerContainer}>
                <div style={{ width: '42px', height: '42px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <img 
                    src="/Icon.png" 
                    alt="VS Logo" 
                    style={{ width: '60px', height: '60px', objectFit: 'contain' }} 
                  />
                </div>
                <h1 style={{ ...headerStyles.headerTitle, marginLeft: '40px' }} className="fancy-serif">КОРЗИНА</h1>
                <div style={{ width: '42px', height: '42px' }} />
              </div>

              <div style={cartPageStyles.infoBanner}>
                Вещи хранятся в корзине 14 дней, после чего удаляются автоматически.
              </div>

              {(() => {
                const deletedClothes = clothes.filter((item: any) => item.deletedAt);
                const deletedOutfits = outfits.filter((item: any) => item.deletedAt);
                const deletedCapsules = capsules.filter((item: any) => item.deletedAt);
                const hasDeletedItems = deletedClothes.length > 0 || deletedOutfits.length > 0 || deletedCapsules.length > 0;

                const restoreItem = (id: number, type: 'clothes' | 'outfits' | 'capsules') => {
                  haptic('medium');
                  if (type === 'clothes') {
                    setClothes(clothes.map((item: any) => item.id === id ? { ...item, deletedAt: null } : item));
                  } else if (type === 'outfits') {
                    setOutfits(outfits.map((item: any) => item.id === id ? { ...item, deletedAt: null } : item));
                  } else if (type === 'capsules') {
                    setCapsules(capsules.map((item: any) => item.id === id ? { ...item, deletedAt: null } : item));
                  }
                };

                if (!hasDeletedItems) {
                  return (
                    <div style={cartPageStyles.container}>
                      <div style={cartPageStyles.emptyIcon}></div>
                      <span style={cartPageStyles.emptyText}>Корзина пуста</span>
                      <p style={cartPageStyles.emptySubtext}>Здесь будут отображаться удаленные вами вещи и образы.</p>
                    </div>
                  );
                }

                return (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {deletedOutfits.length > 0 && (
                      <div>
                        <span style={outfitStyles.sectionTitle} className="fancy-serif">Удаленные аутфиты</span>
                        <div style={{ ...galleryStyles.grid, marginTop: '8px' }}>
                          {deletedOutfits.map((outfit: any) => (
                            <div key={outfit.id} style={{ ...galleryStyles.card, position: 'relative' }}>
                              <button 
                                onClick={() => restoreItem(outfit.id, 'outfits')}
                                style={cartPageStyles.restoreBtn}
                                title="Восстановить"
                              >
                                ↩
                              </button>
                              <div style={{ ...outfitStyles.outfitCard, padding: '4px', height: '100px' }}>
                                <div style={outfitStyles.itemsGrid}>
                                  {outfit.items.slice(0, 4).map((item: any, idx: number) => (
                                    <img key={item.id || idx} src={item.img} alt="" style={galleryStyles.gridImage} />
                                  ))}
                                </div>
                              </div>
                              <span style={galleryStyles.cardTitle}>{outfit.name}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {deletedClothes.length > 0 && (
                      <div>
                        <span style={outfitStyles.sectionTitle} className="fancy-serif">Удаленная одежда</span>
                        <div style={{ ...galleryStyles.grid, marginTop: '8px' }}>
                          {deletedClothes.map((item: any) => (
                            <div 
                              key={item.id} 
                              onClick={() => setSelectedItemForView(item)} 
                              style={{ ...galleryStyles.card, position: 'relative', cursor: 'pointer' }}
                            >
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  restoreItem(item.id, 'clothes');
                                }}
                                style={cartPageStyles.restoreBtn}
                              >
                                ↩
                              </button>
                              <div style={galleryStyles.imageWrapper}>
                                <img src={item.img} alt={item.name} style={galleryStyles.cardImage} />
                              </div>
                              <span style={galleryStyles.cardTitle}>{item.name}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })()}
            </div>
          )}
          
          {isSearchOpen && (
            <>
              <div 
                onClick={() => setIsSearchOpen(false)} 
                style={searchModalStyles.backdrop} 
              />
              <div style={searchModalStyles.box}>
                <div style={searchModalStyles.header}>
                  <span className="fancy-serif" style={searchModalStyles.title}>Поиск одежды</span>
                  <button onClick={() => setIsSearchOpen(false)} style={searchModalStyles.closeBtn}>✕</button>
                </div>
                <div style={searchModalStyles.inputWrapper}>
                  <input 
                    type="text" 
                    placeholder="Введите название вещи..." 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    autoFocus
                    style={searchModalStyles.input}
                  />
                  {searchQuery && (
                    <button onClick={() => setSearchQuery('')} style={searchModalStyles.clearBtn}>Очистить</button>
                  )}
                </div>
                <button 
                  onClick={() => {
                    setIsSearchOpen(false);
                    setCurrentScreen('profile'); 
                    haptic('medium');
                  }}
                  style={searchModalStyles.applyBtn}
                >
                  Применить
                </button>
              </div>
            </>
          )}

          {isOutfitCreatorOpen && (
            <div style={drawerStyles.backdrop} onClick={() => setIsOutfitCreatorOpen(false)}>
              <div 
                style={{ ...drawerStyles.drawer, height: '80vh', maxHeight: '80vh', maxWidth: '380px', display: 'flex', flexDirection: 'column' }} 
                onClick={e => e.stopPropagation()}
              >
                <div style={drawerStyles.header}>
                  <h3 style={drawerStyles.headerTitle}>Создать образ</h3>
                  <button onClick={() => setIsOutfitCreatorOpen(false)} style={drawerStyles.closeBtn}>✕</button>
                </div>
                <div style={{ display: 'flex', gap: '8px', padding: '0 24px 12px 24px', overflowX: 'auto', flexShrink: 0, WebkitOverflowScrolling: 'touch' }}>
                  {КАТЕГОРИИ.map((cat) => (
                    <button 
                      key={cat.id}
                      onClick={() => setSelectedCategory(cat.id)}
                      style={{
                        padding: '8px 14px',
                        borderRadius: '20px',
                        border: 'none',
                        backgroundColor: selectedCategory === cat.id ? '#151414' : '#E6E5E3',
                        color: selectedCategory === cat.id ? '#FFFFFF' : '#151414',
                        fontSize: '13px',
                        fontWeight: '500',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                        flexShrink: 0
                      }}
                    >
                      {cat.name}
                    </button>
                  ))}
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: '4px 24px', WebkitOverflowScrolling: 'touch' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', paddingBottom: '16px' }}>
                    {clothes
                      .filter((item: WardrobeItem) => !item.deletedAt && (selectedCategory === 'all' || item.category === selectedCategory))
                      .map((item: WardrobeItem) => (
                        <div 
                          key={item.id} 
                          onClick={() => toggleItemSelection(item)} 
                          style={{ 
                            border: selectedItems.find((i: WardrobeItem) => i.id === item.id) ? '2px solid #151414' : '1px solid #E6E5E3', 
                            borderRadius: '16px', 
                            overflow: 'hidden',
                            cursor: 'pointer',
                            position: 'relative',
                            aspectRatio: '1/1'
                          }}
                        >
                          <img src={item.img} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          {selectedItems.find((i: WardrobeItem) => i.id === item.id) && (
                            <div style={{
                              position: 'absolute',
                              top: '6px',
                              right: '6px',
                              backgroundColor: '#151414',
                              color: '#FFFFFF',
                              borderRadius: '50%',
                              width: '20px',
                              height: '20px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '11px',
                              fontWeight: '600'
                            }}>✓</div>
                          )}
                        </div>
                      ))}
                  </div>
                </div>

                <div style={{ padding: '16px 24px 24px 24px', display: 'flex', flexDirection: 'column', gap: '12px', backgroundColor: '#FFFFFF', borderTop: '1px solid #E6E5E3', flexShrink: 0 }}>
                  <input 
                    placeholder="Название образа" 
                    value={outfitName}
                    onChange={(e) => setOutfitName(e.target.value)} 
                    style={drawerStyles.input} 
                  />
                  <button 
                    style={{ ...drawerStyles.saveBtn, flex: 'none', width: '100%', padding: '10px 0', borderRadius: '12px', fontSize: '14px', fontWeight: '500', letterSpacing: '0.3px', boxSizing: 'border-box' }} 
                    onClick={() => {
                      if (selectedItems.length === 0) {
                        alert('Выберите хотя бы одну вещь для образа');
                        return;
                      }
                      setOutfits([{ 
                        id: Date.now(), 
                        name: outfitName || "Мой образ", 
                        items: selectedItems, 
                        createdAt: new Date().toISOString(), 
                        deletedAt: null 
                      }, ...outfits]);
                      setIsOutfitCreatorOpen(false); 
                      setSelectedItems([]); 
                      setOutfitName('');
                    }}
                  >
                    Сохранить
                  </button>
                </div>
              </div>
            </div>
          )}

          {isDrawerOpen && (
            <div onClick={() => { setIsDrawerOpen(false); setNewName(''); setNewImage(null); setNewCategory(''); setNewSeason(''); setNewColor(''); setNewMaterial(''); setDrawerError(null); }} style={drawerStyles.backdrop} />
          )}

          <div style={{ ...drawerStyles.drawer, display: isDrawerOpen ? 'flex' : 'none' }}>
            <div style={drawerStyles.header}>
              <div style={drawerStyles.headerLeft}>
                <span style={{ fontSize: '20px', color: '#151414', fontWeight: 'bold', marginRight: '6px' }}>+</span>
                <h3 style={drawerStyles.headerTitle}>Новая вещь</h3>
              </div>
              <button onClick={() => { setIsDrawerOpen(false); setNewName(''); setNewImage(null); setNewCategory(''); setNewSeason(''); setNewColor(''); setNewMaterial(''); setDrawerError(null); }} style={drawerStyles.closeBtn}>✕</button>
            </div>

            <div style={drawerStyles.scrollContainer}>
              {!newImage ? (
                <PhotoPicker onImageSelected={(imgData: string) => {
                  setNewImage(imgData);
                }} />
              ) : (
                <div style={{ position: 'relative', width: '100%', aspectRatio: '1/1', borderRadius: '20px', overflow: 'hidden' }}>
                  <img src={newImage} alt="Preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  <button onClick={() => setNewImage(null)} style={{ position: 'absolute', top: '12px', right: '12px', backgroundColor: 'rgba(21, 20, 20, 0.8)', color: '#FFFFFF', border: 'none', borderRadius: '20px', padding: '6px 12px', fontSize: '12px', fontWeight: '600', cursor: 'pointer' }}>Заменить фото</button>
                </div>
              )}

              <input type="text" placeholder="Название вещи" value={newName} onChange={(e) => setNewName(e.target.value)} style={drawerStyles.input} />

              <select value={newCategory} onChange={(e) => setNewCategory(e.target.value)} style={drawerStyles.select}>
                <option value="" disabled selected hidden>Категория</option>
                <option value="top">Верх</option>
                <option value="bottom">Низ</option>
                <option value="shoes">Обувь</option>
                <option value="accessory">Аксессуары</option>
              </select>

              <select value={newSeason} onChange={(e) => setNewSeason(e.target.value)} style={drawerStyles.select}>
                <option value="" disabled selected hidden>Сезон</option>
                {СЕЗОНЫ.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>

              <select value={newColor} onChange={(e) => setNewColor(e.target.value)} style={drawerStyles.select}>
                <option value="" disabled selected hidden>Цвет</option>
                {ЦВЕТА.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>

              <select value={newMaterial} onChange={(e) => setNewMaterial(e.target.value)} style={drawerStyles.select}>
                <option value="" disabled selected hidden>Материал</option>
                {МАТЕРИАЛЫ.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
              
              {drawerError && (
                <div style={{
                  backgroundColor: '#FFF0F0',
                  border: '1px solid #E57373',
                  borderRadius: '12px',
                  padding: '12px 16px',
                  color: '#E57373',
                  fontSize: '13px',
                  fontWeight: '500',
                  textAlign: 'center',
                  fontFamily: 'Inter, sans-serif',
                  marginTop: '4px',
                  animation: 'fadeIn 0.2s ease'
                }}>
                  {drawerError}
                </div>
              )}

              <div style={drawerStyles.actionsContainer}>
                <button 
                  onClick={() => {
                    if (!newImage) { setDrawerError('Добавьте фотографию вещи'); return; }
                    if (!newName.trim()) { setDrawerError('Введите название вещи'); return; }
                    if (!newCategory) { setDrawerError('Выберите категорию вещи'); return; }
                    if (!newSeason) { setDrawerError('Выберите сезон вещи'); return; }
                    if (!newColor) { setDrawerError('Выберите цвет вещи'); return; }
                    if (!newMaterial) { setDrawerError('Выберите материал вещи'); return; }
                    
                    const newItem = {
                      id: Date.now(),
                      name: newName,
                      category: newCategory,
                      season: newSeason,
                      color: newColor,
                      material: newMaterial,
                      img: newImage,
                      createdAt: new Date().toISOString(),
                      deletedAt: null,
                    };

                    setClothes([newItem, ...clothes]);
                    setIsDrawerOpen(false);
                    setNewName('');
                    setNewImage(null);
                    setNewCategory('');
                    setNewSeason('');
                    setNewColor('');
                    setNewMaterial('');
                    setDrawerError(null);
                    haptic('medium');
                    setCurrentScreen('profile'); 
                  }} 
                  style={drawerStyles.saveBtn}
                >
                  Сохранить
                </button>
              </div>
            </div>
          </div>

          {selectedItemForView && (
            <>
              <div 
                onClick={() => setSelectedItemForView(null)} 
                style={itemModalStyles.backdrop} 
              />
              <div style={itemModalStyles.box}>
                <div style={itemModalStyles.header}>
                  <h3 style={itemModalStyles.title} className="fancy-serif">{selectedItemForView.name}</h3>
                  <button onClick={() => setSelectedItemForView(null)} style={itemModalStyles.closeBtn}>✕</button>
                </div>
                <div style={itemModalStyles.imageContainer}>
                  <img src={selectedItemForView.img} alt="" style={itemModalStyles.image} />
                </div>
                <div style={itemModalStyles.tagsContainer}>
                  <div style={itemModalStyles.tagRow}>
                    <span style={itemModalStyles.tagLabel}>Сезон:</span>
                    <span style={itemModalStyles.tagBadge}>
                      {СЕЗОНЫ.find(s => s.id === selectedItemForView.season)?.name || selectedItemForView.season}
                    </span>
                  </div>
                  <div style={itemModalStyles.tagRow}>
                    <span style={itemModalStyles.tagLabel}>Цвет:</span>
                    <span style={itemModalStyles.tagBadge}>
                      {ЦВЕТА.find(c => c.id === selectedItemForView.color)?.name || selectedItemForView.color}
                    </span>
                  </div>
                  <div style={itemModalStyles.tagRow}>
                    <span style={itemModalStyles.tagLabel}>Материал:</span>
                    <span style={itemModalStyles.tagBadge}>
                      {МАТЕРИАЛЫ.find(m => m.id === selectedItemForView.material)?.name || selectedItemForView.material}
                    </span>
                  </div>
                </div>
              </div>
            </>
          )}
          <BottomNavBar currentScreen={currentScreen} onScreenChange={setCurrentScreen} />
    </div>
  );
}

function App() {
  const { initData, isTelegram, haptic } = useTelegram();

  return (
    <AuthProvider initData={initData} isTelegram={isTelegram}>
      <AppContent />
    </AuthProvider>
  );
}

const ProfileGallery = ({ 
  clothes, setClothes, outfits, setOutfits, capsules, setCapsules, 
  searchQuery, setIsSearchOpen, haptic,
  setIsOutfitCreatorOpen, 
  setIsDrawerOpen,
  onItemClick
}: any) => {
  const [activeTab, setActiveTab] = useState<'capsules' | 'outfits' | 'clothes'>('clothes');
  const [capsuleSubTab, setCapsuleSubTab] = useState<'8-3' | '10-5'>('8-3');
  
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: number; type: 'clothes' | 'outfits' | 'capsules' } | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<string>('all');
  const [selectedColor, setSelectedColor] = useState<string>('all');
  const [selectedMaterial, setSelectedMaterial] = useState<string>('all');
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState<string>('all');

  const openDeleteModal = (id: number, type: 'clothes' | 'outfits' | 'capsules') => {
    setDeleteConfirm({ id, type });
  };

  const confirmDelete = () => {
    if (!deleteConfirm) return;
    const { id, type } = deleteConfirm;
    haptic('heavy');
    const now = new Date().toISOString();
    if (type === 'clothes') setClothes(clothes.map((item: any) => item.id === id ? { ...item, deletedAt: now } : item));
    else if (type === 'outfits') setOutfits(outfits.map((item: any) => item.id === id ? { ...item, deletedAt: now } : item));
    else if (type === 'capsules') setCapsules(capsules.map((item: any) => item.id === id ? { ...item, deletedAt: now } : item));
    setDeleteConfirm(null);
  };

  const filteredClothes = clothes.filter((item: WardrobeItem) => 
    !item.deletedAt && 
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
    (selectedCategoryFilter === 'all' || item.category === selectedCategoryFilter) &&
    (selectedSeason === 'all' || item.season === selectedSeason) &&
    (selectedColor === 'all' || item.color === selectedColor) &&
    (selectedMaterial === 'all' || item.material === selectedMaterial)
  );
  
  const filteredOutfits = outfits.filter((item: any) => !item.deletedAt && item.name.toLowerCase().includes(searchQuery.toLowerCase()));
  const filteredCapsules = capsules 
    ? capsules.filter((item: any) => 
        !item.deletedAt && 
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        item.subType === capsuleSubTab
      ) 
    : [];

  return (
    <div style={{ width: '100%', marginTop: '10px' }}>
      <div style={galleryStyles.tabsContainer}>
        {[ { id: 'capsules', label: 'Капсулы' }, { id: 'outfits', label: 'Аутфиты' }, { id: 'clothes', label: 'Одежда' } ].map((tab) => (
          <button key={tab.id} onClick={() => { setActiveTab(tab.id as any); haptic('light'); }} style={{ ...galleryStyles.tabButton, color: activeTab === tab.id ? '#151414' : '#8B8A89', borderBottom: activeTab === tab.id ? '2px solid #151414' : '2px solid transparent' }}>
            {tab.label}
          </button>
        ))}
      </div>
      
      {activeTab === 'clothes' && (
        <>
          <button 
            style={{
              width: '100%', 
              padding: '12px', 
              marginBottom: '16px', 
              borderRadius: '14px', 
              border: 'none', 
              backgroundColor: '#151414', 
              color: '#FFFFFF', 
              fontWeight: '600',
              fontSize: '13px',
              cursor: 'pointer'
            }} 
            onClick={() => {
              setIsDrawerOpen(true);
              haptic('light');
            }}
          >
            + Добавить вещь
          </button>

          <div style={{ ...galleryStyles.filterRow, gridTemplateColumns: '1fr 1fr 1fr 1fr auto' }}>
            <select 
              onChange={(e) => setSelectedCategoryFilter(e.target.value)} 
              style={galleryStyles.filterSelect}
            >
              <option value="all">Категория</option>
              <option value="top">Верх</option>
              <option value="bottom">Низ</option>
              <option value="shoes">Обувь</option>
              <option value="accessory">Аксессуары</option>
            </select>
            <select onChange={(e) => setSelectedSeason(e.target.value)} style={galleryStyles.filterSelect}><option value="all">Сезон</option>{СЕЗОНЫ.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select>
            <select onChange={(e) => setSelectedColor(e.target.value)} style={galleryStyles.filterSelect}><option value="all">Цвет</option>{ЦВЕТА.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select>
            <select onChange={(e) => setSelectedMaterial(e.target.value)} style={galleryStyles.filterSelect}><option value="all">Материал</option>{МАТЕРИАЛЫ.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}</select>
            <button style={galleryStyles.searchCircle} onClick={() => setIsSearchOpen(true)}><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#151414" strokeWidth="2.5" strokeLinecap="round"><circle cx="11" cy="12" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg></button>
          </div>
        </>
      )}

      {activeTab === 'clothes' && (
        <div style={galleryStyles.itemCount}>
          Всего вещей: {filteredClothes.length}
        </div>
      )}
      
      {activeTab === 'capsules' && (
        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <button
            onClick={() => { setCapsuleSubTab('8-3'); haptic('light'); }}
            style={{
              flex: 1,
              padding: '10px',
              borderRadius: '12px',
              border: 'none',
              backgroundColor: capsuleSubTab === '8-3' ? '#151414' : '#FFFFFF',
              color: capsuleSubTab === '8-3' ? '#FFFFFF' : '#151414',
              fontSize: '13px',
              fontWeight: '500',
              cursor: 'pointer',
              boxShadow: '0px 2px 8px rgba(0,0,0,0.03)',
              transition: 'all 0.2s ease'
            }}
          >
            Капсулы 8-3
          </button>
          <button
            onClick={() => { setCapsuleSubTab('10-5'); haptic('light'); }}
            style={{
              flex: 1,
              padding: '10px',
              borderRadius: '12px',
              border: 'none',
              backgroundColor: capsuleSubTab === '10-5' ? '#151414' : '#FFFFFF',
              color: capsuleSubTab === '10-5' ? '#FFFFFF' : '#151414',
              fontSize: '13px',
              fontWeight: '500',
              cursor: 'pointer',
              boxShadow: '0px 2px 8px rgba(0,0,0,0.03)',
              transition: 'all 0.2s ease'
            }}
          >
            Капсулы 10-5
          </button>
        </div>
      )}

      {activeTab === 'outfits' && (
        <button style={{width: '100%', padding: '12px', marginBottom: '16px', borderRadius: '14px', border: 'none', backgroundColor: '#151414', color: '#FFFFFF', fontWeight: '600'}} onClick={() => setIsOutfitCreatorOpen(true)}>+ Создать новый аутфит</button>
      )}

      {activeTab === 'capsules' && (
        <button 
          style={{width: '100%', padding: '12px', marginBottom: '16px', borderRadius: '14px', border: 'none', backgroundColor: '#151414', color: '#FFFFFF', fontWeight: '600', fontSize: '13px'}} 
          onClick={() => alert(`Тут будет логика создания для капсулы ${capsuleSubTab}`)}
        >
          + Создать капсулу {capsuleSubTab}
        </button>
      )}

      <div style={galleryStyles.grid} className="profile-grid">
        {activeTab === 'capsules' && filteredCapsules.map((capsule: any) => (
          <div key={capsule.id} style={galleryStyles.card}>
            <button onClick={(e) => { e.stopPropagation(); openDeleteModal(capsule.id, 'capsules'); }} style={galleryStyles.deleteBadge}>✕</button>
            <div style={galleryStyles.outfitPreviewGrid}>
              {capsule.items && capsule.items.slice(0, 4).map((item: any, idx: number) => (
                <img key={item.id || idx} src={item.img} style={galleryStyles.gridImage} alt="" />
              ))}
            </div>
            <span style={galleryStyles.cardTitle}>{capsule.name}</span>
          </div>
        ))}

        {activeTab === 'clothes' && (
          filteredClothes.length > 0 ? (
            filteredClothes.map((item: any) => (
              <div 
                key={item.id} 
                onClick={() => onItemClick(item)} 
                style={{ ...galleryStyles.card, position: 'relative', cursor: 'pointer' }}
              >
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    openDeleteModal(item.id, 'clothes');
                  }}
                  style={galleryStyles.deleteBadge}
                >
                  ✕
                </button>
                <div style={galleryStyles.imageWrapper}>
                  <img src={item.img} alt={item.name} style={galleryStyles.cardImage} />
                </div>
                <span style={galleryStyles.cardTitle}>{item.name}</span>
              </div>
            ))
          ) : (
            <div style={galleryStyles.emptyState}>
              {searchQuery.trim() !== '' ? 'Ничего не найдено по этому запросу' : 'Гардероб пуст. Сначала добавьте вещи'}
            </div>
          )
        )}

        {activeTab === 'outfits' && filteredOutfits.map((outfit: any) => (
          <div key={outfit.id} style={galleryStyles.card}>
            <button onClick={(e) => { e.stopPropagation(); openDeleteModal(outfit.id, 'outfits'); }} style={galleryStyles.deleteBadge}>✕</button>
            <div style={{ ...outfitStyles.outfitCard, padding: '4px', height: '100px' }}>
              <div style={outfitStyles.itemsGrid}>
                {outfit.items.map((item: WardrobeItem, idx: number) => (
                  <img key={idx} src={item.img} style={galleryStyles.gridImage} />
                ))}
              </div>
            </div>
            <span style={galleryStyles.cardTitle}>{outfit.name}</span>
          </div>
        ))}
      </div>

      {deleteConfirm && (
        <>
          <div onClick={() => setDeleteConfirm(null)} style={galleryStyles.confirmBackdrop} />
          <div style={galleryStyles.confirmBox}>
            <span style={galleryStyles.confirmText}>Переместить в корзину?</span>
            <div style={galleryStyles.confirmActions}>
              <button onClick={confirmDelete} style={galleryStyles.confirmDeleteBtn}>Да</button>
              <button onClick={() => setDeleteConfirm(null)} style={galleryStyles.confirmCancelBtn}>Отмена</button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

const pageStyle: React.CSSProperties = {
  width: '100%',
  minHeight: '100vh',
  padding: '16px 16px 120px 16px',
  boxSizing: 'border-box',
};

const navStyles: Record<string, React.CSSProperties> = {
  navBarContainer: {
    position: 'fixed',
    bottom: '24px',
    left: '0',
    right: '0',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9999,
    pointerEvents: 'none',
  },
  navBar: {
    display: 'flex',
    backgroundColor: '#151414',
    borderRadius: '24px', 
    padding: '12px 24px',
    alignItems: 'center',
    boxShadow: '0px 10px 30px rgba(0, 0, 0, 0.3)',
    pointerEvents: 'auto',
    width: 'auto',
    maxWidth: '240px',
    gap: '48px',
    justifyContent: 'center',
    boxSizing: 'border-box',
    margin: '0 auto',
  },
  navButton: {
    background: 'none',
    border: 'none',
    outline: 'none',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    padding: '4px 0',
    width: '44px',
    height: '44px',
  },
  activeIndicator: {
    position: 'absolute',
    bottom: '-2px',
    width: '20px',
    height: '2px',
    backgroundColor: '#FFFFFF',
    borderRadius: '1px',
  },
};

const drawerStyles: Record<string, React.CSSProperties> = {
  backdrop: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    zIndex: 998,
  },
  drawer: {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '90%',
    maxWidth: '360px',
    maxHeight: '85vh',
    backgroundColor: '#FFFFFF',
    borderRadius: '28px',
    boxShadow: '0px 12px 40px rgba(0, 0, 0, 0.15)',
    zIndex: 999,
    display: 'flex',
    flexDirection: 'column',
    boxSizing: 'border-box',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 24px 12px 24px',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  headerTitle: {
    margin: 0,
    fontSize: '22px',
    fontWeight: '700',
    color: '#333231',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    fontSize: '22px',
    color: '#151414',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  scrollContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '0 24px 24px 24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  photoPickerZone: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '32px 24px',
    backgroundColor: '#E6E5E3',
    borderRadius: '20px',
    border: '1.5px dashed #D4D3D1',
    gap: '12px',
    cursor: 'pointer',
  },
  pickerCircle: {
    width: '44px',
    height: '44px',
    borderRadius: '50%',
    backgroundColor: '#FFFFFF',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  input: {
    width: '100%',
    padding: '14px 18px',
    borderRadius: '14px',
    border: 'none',
    backgroundColor: '#E6E5E3',
    color: '#151414',
    fontSize: '16px',
    boxSizing: 'border-box',
    outline: 'none',
  },
  select: {
    width: '100%',
    padding: '14px 18px',
    borderRadius: '14px',
    border: 'none',
    backgroundColor: '#E6E5E3',
    color: '#151414',
    fontSize: '16px',
    boxSizing: 'border-box',
    outline: 'none',
    appearance: 'none',
    backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23151414' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'></polyline></svg>")`,
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'right 18px center',
    backgroundSize: '16px',
  },
  actionsContainer: {
    display: 'flex',
    gap: '12px',
    marginTop: '8px',
  },
  saveBtn: {
    flex: 1,
    padding: '16px',
    backgroundColor: '#323130',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '16px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  cancelBtn: {
    flex: 1,
    padding: '16px',
    backgroundColor: '#D4D3D1',
    color: '#151414',
    border: 'none',
    borderRadius: '16px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
  },
};

const headerStyles: Record<string, React.CSSProperties> = {
  headerContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    padding: '8px 4px 16px 4px',
    boxSizing: 'border-box',
    backgroundColor: 'transparent',
  },
  headerTitle: {
    margin: 0,
    fontSize: '22px',
    fontWeight: '600',
    color: '#151414',
    textAlign: 'center',
    flex: 1,
    marginRight: '35px',
  },
  logoZone: {
    position: 'relative',
    width: '40px',
    height: '40px',
    userSelect: 'none',
  },
  searchBtn: {
    width: '42px',
    height: '42px',
    borderRadius: '50%',
    backgroundColor: '#151414',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.1)',
  },
};

const outfitStyles: Record<string, React.CSSProperties> = {
  sectionContainer: {
    width: '100%',
    marginTop: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    boxSizing: 'border-box',
  },
  sectionTitle: {
    margin: 0,
    fontSize: '15px',
    fontWeight: '600',
    color: '#151414',
  },
  mainRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr', 
    gridTemplateRows: '140px 170px', 
    gap: '12px', 
    width: '100%',
    boxSizing: 'border-box',
  },
  outfitCard: {
    gridRow: '1 / span 2', 
    backgroundColor: '#FFFFFF',
    borderRadius: '24px',
    padding: '16px',
    boxSizing: 'border-box',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0px 4px 16px rgba(0, 0, 0, 0.03)',
  },
  outfitName: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#6B6A69',
    marginBottom: '12px',
    display: 'block',
  },
  itemsGrid: {
    flex: 1,
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '8px',
    alignItems: 'center',
  },
  emptyGrid: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    borderRadius: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: '1px dashed #D4D3D1',
  },
  gridImage: {
    width: '100%',
    aspectRatio: '1/1',
    objectFit: 'cover',
    borderRadius: '12px',
    backgroundColor: '#E6E5E3',
  },
};

const homeStyles: Record<string, React.CSSProperties> = {
  buttonContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'flex-start',
    paddingTop: '85px',
    boxSizing: 'border-box',
  },
  addBtn: {
    background: 'none',
    border: 'none',
    outline: 'none',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '16px', 
    padding: '20px',
  },
  plusCircle: {
    width: '72px',
    height: '72px',
    borderRadius: '50%',
    border: '2px solid #151414', 
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    transition: 'transform 0.2s ease',
  },
  btnText: {
    color: '#151414',
    fontSize: '16px',
    fontWeight: '600',
  },
};

const widgetStyles: Record<string, React.CSSProperties> = {
  weatherCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: '20px',
    padding: '12px 14px',
    color: '#151414',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    boxSizing: 'border-box',
    height: '100%',
    boxShadow: '0px 4px 16px rgba(0, 0, 0, 0.03)',
  },
  hourlyRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: 'auto',
    borderTop: '0.5px solid rgba(21, 20, 20, 0.12)',
    paddingTop: '8px',
  },
  weatherCity: {
    fontSize: '12px',
    fontWeight: '600',
    opacity: 0.9,
  },
  weatherTemp: {
    fontSize: '32px',
    fontWeight: '700',
    margin: '6px 0',
  },
  hourItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    fontSize: '9px',
    gap: '1px',
  },
  calendarCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: '20px',
    padding: '10px',
    display: 'flex',
    flexDirection: 'column',
    boxSizing: 'border-box',
    boxShadow: '0px 4px 16px rgba(0, 0, 0, 0.03)',
    height: '100%',
    justifyContent: 'space-between',
  },
  calendarDaysHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '8px',
    fontWeight: '700',
    color: '#A8A7A5',
    textAlign: 'center',
  },
  calendarGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(7, 1fr)', 
    rowGap: '6px', 
    columnGap: '2px',
    marginTop: '6px',
  },
  dayCell: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    aspectRatio: '1/1',
    width: '18px',
    height: '18px',
    margin: '0 auto',
    boxSizing: 'border-box',
  },
  dayNumber: {
    fontSize: '10px',
    fontWeight: '500',
    color: '#151414',
  },
};

const galleryStyles: Record<string, React.CSSProperties> = {
  tabsContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    borderBottom: '1px solid rgba(21, 20, 20, 0.08)',
    paddingBottom: '4px',
    marginBottom: '20px',
  },
  tabButton: {
    background: 'none',
    border: 'none',
    outline: 'none',
    padding: '10px 12px',
    fontSize: '15px',
    cursor: 'pointer',
    fontFamily: 'Inter, sans-serif',
    transition: 'all 0.2s ease',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)', 
    gap: '10px',
    width: '100%',
    boxSizing: 'border-box',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: '14px',
    padding: '6px',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.02)',
    boxSizing: 'border-box',
    position: 'relative',
  },
  imageWrapper: {
    width: '100%',
    aspectRatio: '1/1',
    borderRadius: '10px',
    overflow: 'hidden',
    backgroundColor: '#E6E5E3',
  },
  cardImage: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  cardTitle: {
    fontSize: '11px',
    fontWeight: '500',
    color: '#151414',
    paddingLeft: '2px',
    textOverflow: 'ellipsis',
    overflow: 'hidden',
    whiteSpace: 'nowrap',
  },
  itemCount: {
    fontSize: '11px',
    color: '#8B8A89',
    fontWeight: '500',
    marginTop: '4px',
    marginBottom: '12px',
    paddingLeft: '2px',
    fontFamily: 'Inter, sans-serif',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  outfitPreviewGrid: {
    width: '100%',
    aspectRatio: '1/1',
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '3px',
    backgroundColor: '#E6E5E3',
    borderRadius: '10px',
    padding: '3px',
    boxSizing: 'border-box',
  },
  gridImage: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    borderRadius: '6px',
  },
  emptyState: {
    gridColumn: '1 / -1', 
    textAlign: 'center',
    padding: '40px 20px',
    color: '#6B6A69',
    fontSize: '14px',
  },
  deleteBadge: {
    position: 'absolute',
    top: '10px',
    right: '10px',
    width: '18px',
    height: '18px',
    borderRadius: '50%',
    backgroundColor: 'rgba(21, 20, 20, 0.75)',
    color: '#FFFFFF',
    border: 'none',
    outline: 'none',
    fontSize: '9px',
    fontWeight: 'bold',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    zIndex: 10,
    transition: 'background-color 0.2s ease',
  },
  confirmBackdrop: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    zIndex: 99998,
  },
  confirmBox: {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '85%',
    maxWidth: '320px',
    backgroundColor: '#FFFFFF',
    borderRadius: '24px',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    boxShadow: '0px 16px 40px rgba(0, 0, 0, 0.12)',
    zIndex: 99999,
    boxSizing: 'border-box',
    textAlign: 'center',
  },
  confirmText: {
    fontSize: '16px',
    fontWeight: '500',
    color: '#151414',
    lineHeight: '1.4',
    fontFamily: 'Inter, sans-serif',
  },
  confirmActions: {
    display: 'flex',
    gap: '10px',
  },
  confirmDeleteBtn: {
    flex: 1,
    padding: '14px',
    backgroundColor: '#E57373',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '14px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  confirmCancelBtn: {
    flex: 1,
    padding: '14px',
    backgroundColor: '#E6E5E3',
    color: '#151414',
    border: 'none',
    borderRadius: '14px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  tabsAndSearch: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  filterRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr 1fr auto',
    gap: '8px',
    marginBottom: '16px',
    alignItems: 'center',
  },
  filterSelect: {
    width: '100%',
    padding: '8px 24px 8px 8px',
    borderRadius: '10px',
    border: 'none',
    backgroundColor: '#FFFFFF',
    fontSize: '11px',
    color: '#151414',
    outline: 'none',
    cursor: 'pointer',
    fontFamily: 'Inter, sans-serif',
    boxShadow: '0px 2px 8px rgba(0,0,0,0.03)',
    textAlign: 'left',
    appearance: 'none',
    WebkitAppearance: 'none',
    MozAppearance: 'none',
    backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23151414' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'></polyline></svg>")`,
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'right 8px center',
  },
  searchCircle: {
    flexShrink: 0,
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    backgroundColor: '#FFFFFF',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    boxShadow: '0px 2px 8px rgba(0,0,0,0.05)',
  },
};

const searchModalStyles: Record<string, React.CSSProperties> = {
  backdrop: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    zIndex: 99998,
  },
  box: {
    position: 'fixed',
    top: '40%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '85%',
    maxWidth: '340px',
    backgroundColor: '#FFFFFF',
    borderRadius: '24px',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    boxShadow: '0px 16px 40px rgba(0, 0, 0, 0.15)',
    zIndex: 99999,
    boxSizing: 'border-box',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '4px',
  },
  title: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#151414',
    letterSpacing: '1px',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    fontSize: '18px',
    color: '#8B8A89',
    cursor: 'pointer',
    padding: '4px',
  },
  inputWrapper: {
    position: 'relative',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
  },
  input: {
    width: '100%',
    padding: '14px 16px',
    paddingRight: '80px',
    borderRadius: '14px',
    border: 'none',
    backgroundColor: '#E6E5E3',
    color: '#151414',
    fontSize: '15px',
    boxSizing: 'border-box',
    outline: 'none',
    fontFamily: 'Inter, sans-serif',
  },
  clearBtn: {
    position: 'absolute',
    right: '12px',
    background: 'none',
    border: 'none',
    color: '#6B6A69',
    fontSize: '12px',
    fontWeight: '500',
    cursor: 'pointer',
  },
  applyBtn: {
    width: '100%',
    padding: '14px',
    backgroundColor: '#151414',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '14px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
};

const cartPageStyles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '80px 24px',
    textAlign: 'center',
    boxSizing: 'border-box',
  },
  infoBanner: {
    backgroundColor: '#FFFFFF',
    borderRadius: '14px',
    padding: '12px 16px',
    fontSize: '13px',
    color: '#6B6A69',
    textAlign: 'center',
    marginBottom: '20px',
    lineHeight: '1.4',
    border: '1px solid rgba(21, 20, 20, 0.05)',
    fontFamily: 'Inter, sans-serif',
  },
  emptyText: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#151414',
    marginBottom: '8px',
    fontFamily: 'Inter, sans-serif',
  },
  emptySubtext: {
    fontSize: '14px',
    color: '#6B6A69',
    lineHeight: '1.5',
    margin: '0',
    maxWidth: '260px',
    fontFamily: 'Inter, sans-serif',
  },
  restoreBtn: {
    position: 'absolute',
    top: '10px',
    right: '10px',
    width: '20px',
    height: '20px',
    borderRadius: '50%',
    backgroundColor: '#151414',
    color: '#FFFFFF',
    border: 'none',
    outline: 'none',
    fontSize: '11px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    zIndex: 10,
  },
};

const itemModalStyles: Record<string, React.CSSProperties> = {
  backdrop: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    zIndex: 99998,
  },
  box: {
    position: 'fixed',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '85%',
    maxWidth: '340px',
    backgroundColor: '#FFFFFF',
    borderRadius: '24px',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    boxShadow: '0px 16px 40px rgba(0, 0, 0, 0.15)',
    zIndex: 99999,
    boxSizing: 'border-box',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    margin: 0,
    fontSize: '18px',
    fontWeight: '600',
    color: '#151414',
    textTransform: 'uppercase',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    fontSize: '18px',
    color: '#8B8A89',
    cursor: 'pointer',
  },
  imageContainer: {
    width: '100%',
    aspectRatio: '1/1',
    borderRadius: '16px',
    overflow: 'hidden',
    backgroundColor: '#E6E5E3',
  },
  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
  tagsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginTop: '4px',
  },
  tagRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '4px 0',
    borderBottom: '0.5px solid rgba(21, 20, 20, 0.05)',
  },
  tagLabel: {
    fontSize: '13px',
    color: '#8B8A89',
    fontFamily: 'Inter, sans-serif',
  },
  tagBadge: {
    fontSize: '13px',
    fontWeight: '600',
    color: '#151414',
    backgroundColor: '#E6E5E3',
    padding: '4px 10px',
    borderRadius: '8px',
    fontFamily: 'Inter, sans-serif',
  },
};

export default App;
export { getTheme, СЕЗОНЫ, ЦВЕТА, МАТЕРИАЛЫ, КАТЕГОРИИ, useMediaQuery, useTelegram };