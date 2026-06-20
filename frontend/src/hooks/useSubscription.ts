import { useState, useEffect } from 'react';
import { useLocalStorage } from './useLocalStorage';

const FREE_ITEMS_LIMIT = 15;

export function useSubscription() {
  const [isPremium, setIsPremium] = useLocalStorage('is_premium', false);
  const [subscriptionExpiry, setSubscriptionExpiry] = useLocalStorage<string | null>('subscription_expiry', null);
  const [showPayModal, setShowPayModal] = useState(false);

  useEffect(() => {
    if (subscriptionExpiry && new Date(subscriptionExpiry) < new Date()) {
      setIsPremium(false);
      setSubscriptionExpiry(null);
    }
  }, [subscriptionExpiry]);

  const canAddItem = (currentItemsCount: number): boolean => {
    if (isPremium) return true;
    if (currentItemsCount < FREE_ITEMS_LIMIT) return true;
    setShowPayModal(true);
    return false;
  };

  const getRemainingFreeSlots = (currentItemsCount: number): number => {
    if (isPremium) return Infinity;
    return Math.max(0, FREE_ITEMS_LIMIT - currentItemsCount);
  };

  const activatePremium = () => {
    setIsPremium(true);
    const expiryDate = new Date();
    expiryDate.setMonth(expiryDate.getMonth() + 1);
    setSubscriptionExpiry(expiryDate.toISOString());
    setShowPayModal(false);
    alert('Premium активирован! Теперь можно добавлять неограниченное количество вещей.');
  };

  return {
    isPremium,
    showPayModal,
    setShowPayModal,
    canAddItem,
    getRemainingFreeSlots,
    activatePremium,
    freeLimit: FREE_ITEMS_LIMIT,
  };
}
