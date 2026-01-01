import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { ShopStoreStateType } from './types';

export const useShopStore = create<ShopStoreStateType>()(
  devtools((set) => ({
    shops: [],
    currentShop: null,
    setCurrentShop: (shop) => set({ currentShop: shop }, undefined, 'setCurrentShop'),
    addShops: (shops) =>
      set((state) => ({ shops: [...state.shops, ...shops] }), undefined, 'addShops'),
    updateShop: (shop) =>
      set(
        (state) => ({
          shops: state.shops.map((s) => (s.id === shop.id ? shop : s)),
        }),
        undefined,
        'updateShop'
      ),
    deleteShop: (id) =>
      set((state) => ({ shops: state.shops.filter((s) => s.id !== id) }), undefined, 'deleteShop'),
  }))
);
