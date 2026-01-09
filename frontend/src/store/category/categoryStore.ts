import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { CategorySimpleType, CategoryStoreStateType } from './types';

export const useCategoryStore = create<CategoryStoreStateType>()(
  devtools((set) => ({
    categories: null,
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
