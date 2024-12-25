export type ShopType<C> = {
  id?: number | null;
  category: C;
  name: string;
  icon: string | null;
  description: string;
};

export type ShopAddressType<S> = {
  id?: number | null;
  shop: S;
  address: string;
  local_name: string;
};

export type ShopProps = {
  shops: ShopType<number>[];
  addresses: ShopAddressType<number>[];
};
