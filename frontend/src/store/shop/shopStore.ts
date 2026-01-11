import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { ShopSimpleType, ShopStoreStateType } from './types';

export const useShopStore = create<ShopStoreStateType>()(
  devtools((set) => ({
    shops: null,
    currentShop: null,
    addresses: null,
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
    addCurrentShopAddress: (address) =>
      set(
        (state) => {
          if (!state.currentShop) return state;
          return {
            addresses: state.addresses === null ? null : [...state.addresses, address],
            currentShop: {
              ...state.currentShop,
              addresses: [...state.currentShop.addresses, address],
            },
          };
        },
        undefined,
        'addCurrentShopAddress'
      ),
    updateCurrentShopAddress: (address) =>
      set(
        (state) => {
          if (!state.currentShop) return state;
          return {
            addresses:
              state.addresses === null
                ? null
                : state.addresses.map((a) => (a.id === address.id ? address : a)),
            currentShop: {
              ...state.currentShop,
              addresses: state.currentShop.addresses.map((a) =>
                a.id === address.id ? address : a
              ),
            },
          };
        },
        undefined,
        'updateCurrentShopAddress'
      ),
    deleteCurrentShopAddress: (id) =>
      set(
        (state) => {
          if (!state.currentShop) return state;
          return {
            addresses: state.addresses === null ? null : state.addresses.filter((a) => a.id !== id),
            currentShop: {
              ...state.currentShop,
              addresses: state.currentShop.addresses.filter((a) => a.id !== id),
            },
          };
        },
        undefined,
        'deleteCurrentShopAddress'
      ),
    setAddresses: (addresses) => set({ addresses: addresses }, undefined, 'setAddresses'),
  }))
);
