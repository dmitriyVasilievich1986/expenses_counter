export type ShopSimpleType = {
  id: number;
  name: string;
  description: string | null;
  icon: string | null;
  categoryId: number | null;
};

export type ShopType = ShopSimpleType;

export type ShopStoreStateType = {
  shops: ShopSimpleType[];
  addShops: (shops: ShopSimpleType[]) => void;
  updateShop: (shop: ShopSimpleType) => void;
  deleteShop: (id: number) => void;
};
