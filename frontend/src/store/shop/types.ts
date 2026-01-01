import type { CategorySimpleType } from '../category/types';

export type AddressSimpleType = {
  id: number;
  address: string;
  localName: string;
};

export type ShopSimpleType = {
  id: number;
  name: string;
  description: string | null;
  icon: string | null;
  categoryId: number | null;
};

export type ShopType = ShopSimpleType & {
  category: CategorySimpleType;
  addresses: AddressSimpleType[];
};

export type ShopStoreStateType = {
  currentShop: ShopType | null;
  shops: ShopSimpleType[];
  addShops: (shops: ShopSimpleType[]) => void;
  updateShop: (shop: ShopSimpleType) => void;
  deleteShop: (id: number) => void;
  setCurrentShop: (shop: ShopType | null) => void;
};
