/**
 * Barrel module for the product Zustand store: re-exports {@link useProductStore} and public entity types from `./types`.
 */

import { useProductStore } from './productStore';

import type { ProductSimpleType, ProductType } from './types';

export { useProductStore, type ProductSimpleType, type ProductType };
