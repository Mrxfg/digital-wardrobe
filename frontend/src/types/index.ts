
export interface ClothesItem {
  id: number;
  name: string;
  category: 'top' | 'bottom' | 'shoes' | 'accessory';
  season: 'Зима' | 'Лето' | 'Осень' | 'Весна' | 'Демисезон';
  img: string;
  usageType?: 'повседневная' | 'редкая' | 'на выход';
  createdAt: string;
  deletedAt?: string | null;
}

export interface Outfit {
  id: number;
  name: string;
  top?: ClothesItem;
  bottom?: ClothesItem;
  shoes?: ClothesItem;
  accessory?: ClothesItem;
  createdAt: string;
}

export interface Capsule {
  id: number;
  type: '8-3' | '10-5';
  items: ClothesItem[];
  outfits: Outfit[];
  createdAt: string;
}

export interface WearHistory {
  date: string;
  itemId: number;
}

export interface User {
  id: number;
  telegramId: string;
  username: string;
  firstName?: string;
  lastName?: string;
  photoUrl?: string;
  createdAt: string;
}

export type CategoryType = 'top' | 'bottom' | 'shoes' | 'accessory';
export type SeasonType = 'Зима' | 'Лето' | 'Осень' | 'Весна' | 'Демисезон';
export type UsageType = 'повседневная' | 'редкая' | 'на выход';
export type ScreenType = 'wardrobe' | 'constructor' | 'calendar';

export interface WardrobeGridProps {
  clothes: ClothesItem[];
  setClothes: (clothes: ClothesItem[]) => void;
  history: WearHistory[];
}

export interface AddItemModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (item: ClothesItem) => void;
}

export interface TrashBinProps {
  isOpen: boolean;
  onClose: () => void;
  clothes: ClothesItem[];
  setClothes: (clothes: ClothesItem[]) => void;
}

export interface CapsuleWizardProps {
  clothes: ClothesItem[];
  outfits: Outfit[];
  setOutfits: (outfits: Outfit[]) => void;
}

export interface WearCalendarProps {
  clothes: ClothesItem[];
  history: WearHistory[];
  setHistory: (history: WearHistory[]) => void;
}
