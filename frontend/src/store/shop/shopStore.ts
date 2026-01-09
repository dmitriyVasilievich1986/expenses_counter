import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { ShopSimpleType, ShopStoreStateType } from './types';

export const useShopStore = create<ShopStoreStateType>()(
  devtools((set) => ({
    shops: null,
    currentShop: null,
    setCurrentShop: (shop) => set({ currentShop: shop }, undefined, 'setCurrentShop'),
    addShops: (shops) =>
      set((state) => ({ shops: [...(state.shops ?? []), ...shops] }), undefined, 'addShops'),
    updateShop: (shop) =>
      set(
        (state) => ({
          shops: (state.shops as ShopSimpleType[]).map((s) => (s.id === shop.id ? shop : s)),
        }),
        undefined,
        'updateShop'
      ),
    deleteShop: (id) =>
      set(
        (state) => ({ shops: (state.shops as ShopSimpleType[]).filter((s) => s.id !== id) }),
        undefined,
        'deleteShop'
      ),
    addAddress: (address) =>
      set(
        (state) => {
          if (!state.currentShop) return state;
          return {
            currentShop: {
              ...state.currentShop,
              addresses: [...state.currentShop.addresses, address],
            },
          };
        },
        undefined,
        'addAddress'
      ),
    updateAddress: (address) =>
      set(
        (state) => {
          if (!state.currentShop) return state;
          return {
            currentShop: {
              ...state.currentShop,
              addresses: state.currentShop.addresses.map((a) =>
                a.id === address.id ? address : a
              ),
            },
          };
        },
        undefined,
        'updateAddress'
      ),
    deleteAddress: (id) =>
      set(
        (state) => {
          if (!state.currentShop) return state;
          return {
            currentShop: {
              ...state.currentShop,
              addresses: state.currentShop.addresses.filter((a) => a.id !== id),
            },
          };
        },
        undefined,
        'deleteAddress'
      ),
  }))
);
