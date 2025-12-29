import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { CategoryStoreStateType } from './types';

export const useCategoryStore = create<CategoryStoreStateType>()(
  devtools((set) => ({
    categories: [],
    addCategories: (categories) =>
      set(
        (state) => ({ categories: [...state.categories, ...categories] }),
        undefined,
        'addCategories'
      ),
    updateCategory: (category) =>
      set(
        (state) => ({
          categories: state.categories.map((c) => (c.id === category.id ? category : c)),
        }),
        undefined,
        'updateCategory'
      ),
    deleteCategory: (id) =>
      set(
        (state) => ({
          categories: state.categories.filter((c) => c.id !== id),
        }),
        undefined,
        'deleteCategory'
      ),
  }))
);
