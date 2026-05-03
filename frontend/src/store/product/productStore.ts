/**
 * Zustand store for products: paginated list state and the product currently in focus.
 *
 * Wrapped with Redux DevTools middleware for debugging.
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { ProductSimpleType, ProductStoreStateType } from './types';

/** Hook returning product store state and actions (see {@link ProductStoreStateType}). */
export const useProductStore = create<ProductStoreStateType>()(
  devtools((set) => ({
    products: null,
    currentProduct: null,
    totalProducts: 0,
    productListLoading: false,
    setCurrentProduct: (product) =>
      set({ currentProduct: product }, undefined, 'setCurrentProduct'),
    setProducts: (products, totalProducts) =>
      set({ products: products, totalProducts: totalProducts }, undefined, 'setProducts'),
    setProductListLoading: (loading) =>
      set({ productListLoading: loading }, undefined, 'setProductListLoading'),
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
