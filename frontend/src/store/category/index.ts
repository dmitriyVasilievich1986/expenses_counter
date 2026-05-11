/**
 * Barrel module for the category Zustand store: re-exports {@link useCategoryStore} and public entity types from `./types`.
 */

import { useCategoryStore } from './categoryStore';

import type { CategorySimpleType, CategoryType } from './types';

export { useCategoryStore, type CategorySimpleType, type CategoryType };
