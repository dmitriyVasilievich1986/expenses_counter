import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { ProductSimpleType, ProductStoreStateType } from './types';

export const useProductStore = create<ProductStoreStateType>()(
  devtools((set) => ({
    products: null,
    currentProduct: null,
    setCurrentProduct: (product) =>
      set({ currentProduct: product }, undefined, 'setCurrentProduct'),
    addProducts: (products) =>
      set(
        (state) => ({ products: [...(state.products ?? []), ...products] }),
        undefined,
        'addProducts'
      ),
    updateProduct: (product) =>
      set(
        (state) => ({
          products: (state.products as ProductSimpleType[]).map((p) =>
            p.id === product.id ? product : p
          ),
        }),
        undefined,
        'updateProduct'
      ),
    deleteProduct: (id) =>
      set(
        (state) => ({
          products: (state.products as ProductSimpleType[]).filter((p) => p.id !== id),
        }),
        undefined,
        'deleteProduct'
      ),
  }))
);
