/**
 * Zustand store for shops: paginated list state, the shop currently in focus,
 * and address lists kept in sync with `currentShop`.
 *
 * Wrapped with Redux DevTools middleware for debugging.
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { ShopSimpleType, ShopStoreStateType } from './types';

/** Hook returning shop store state and actions (see {@link ShopStoreStateType}). */
export const useShopStore = create<ShopStoreStateType>()(
  devtools((set) => ({
    shops: null,
    currentShop: null,
    totalShops: 0,
    shopListLoading: false,
    addresses: null,
    setCurrentShop: (shop) => set({ currentShop: shop }, undefined, 'setCurrentShop'),
    setShops: (shops, totalShops) =>
      set({ shops: shops, totalShops: totalShops }, undefined, 'setShops'),
    setShopListLoading: (loading) =>
      set({ shopListLoading: loading }, undefined, 'setShopListLoading'),
    addShops: (shops) =>
      set(
        (state) => ({
          shops: [...(state.shops ?? []), ...shops],
          totalShops: state.totalShops + shops.length,
        }),
        undefined,
        'addShops'
      ),
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
        (state) => ({
          shops: (state.shops as ShopSimpleType[]).filter((s) => s.id !== id),
          totalShops: state.totalShops - 1,
        }),
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
