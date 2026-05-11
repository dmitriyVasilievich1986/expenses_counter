/**
 * Zustand store for categories: in-memory category list (`null` until loaded) and list mutations used by the API client.
 *
 * Wrapped with Redux DevTools middleware for debugging.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { CategorySimpleType, CategoryStoreStateType } from './types';

/** Hook returning category store state and actions (see {@link CategoryStoreStateType}). */
export const useCategoryStore = create<CategoryStoreStateType>()(
  devtools((set) => ({
    categories: null,
    setCategories: (categories) => set({ categories }),
    addCategories: (categories) =>
      set(
        (state) => ({ categories: [...(state.categories ?? []), ...categories] }),
        undefined,
        'addCategories'
      ),
    updateCategory: (category) =>
      set(
        (state) => ({
          categories: (state.categories as CategorySimpleType[]).map((c) =>
            c.id === category.id ? category : c
          ),
        }),
        undefined,
        'updateCategory'
      ),
    deleteCategory: (id) =>
      set(
        (state) => ({
          categories: (state.categories as CategorySimpleType[]).filter((c) => c.id !== id),
        }),
        undefined,
        'deleteCategory'
      ),
  }))
);
