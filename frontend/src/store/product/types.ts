/**
 * Zustand product slice types: entities returned from the API and the combined store state shape.
 */

import type { CategorySimpleType } from '../category/types';

/**
 * Product fields used in list views and lightweight responses (no nested relations).
 *
 * @property {number} id - Product primary key.
 * @property {string} name - Display name.
 * @property {(string | null)} description - Optional description text.
 * @property {number} categoryId - Owning category id.
 */
export type ProductSimpleType = {
  id: number;
  name: string;
  description: string | null;
  categoryId: number;
};

/**
 * Full product entity with nested category (e.g. detail view).
 *
 * @property {CategorySimpleType} category - Resolved category for this product.
 */
export type ProductType = ProductSimpleType & {
  category: CategorySimpleType;
};

/**
 * State and actions exposed by the product Zustand store.
 *
 * @property {(ProductSimpleType[] | null)} products - Cached list page; null until loaded.
 * @property {(ProductType | null)} currentProduct - Product selected for detail/edit flows.
 * @property {(product: ProductType | null) => void} setCurrentProduct - Sets or clears the detail product.
 * @property {(products: ProductSimpleType[]) => void} setProducts - Replaces the list and total count.
 * @property {(loading: boolean) => void} setProductListLoading - Updates list loading flag.
 * @property {(products: ProductSimpleType[]) => void} addProducts - Appends products to the cached list.
 * @property {(product: ProductSimpleType) => void} updateProduct - Merges one product into the cached list by id.
 * @property {(id: number) => void} deleteProduct - Removes a product from the cached list by id.
 */
export type ProductStoreStateType = {
  products: ProductSimpleType[] | null;
  currentProduct: ProductType | null;
  setCurrentProduct: (product: ProductType | null) => void;
  setProducts: (products: ProductSimpleType[]) => void;
  addProducts: (products: ProductSimpleType[]) => void;
  updateProduct: (product: ProductSimpleType) => void;
  deleteProduct: (id: number) => void;
};
