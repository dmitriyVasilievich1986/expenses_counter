import type { CategorySimpleType } from '../category/types';

export type ProductSimpleType = {
  id: number;
  name: string;
  description: string | null;
  categoryId: number;
};

export type ProductType = ProductSimpleType & {
  category: CategorySimpleType;
};

export type ProductStoreStateType = {
  products: ProductSimpleType[] | null;
  currentProduct: ProductType | null;
  setCurrentProduct: (product: ProductType | null) => void;
  addProducts: (products: ProductSimpleType[]) => void;
  updateProduct: (product: ProductSimpleType) => void;
  deleteProduct: (id: number) => void;
};
