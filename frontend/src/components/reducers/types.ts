export type CategoryType = {
  id?: number | null;
  name: string;
  description: string;
  parent: number | null;
};

export type ShopType = {
  id?: number | null;
  name: string;
  description: string;
  category: number | null;
};

export type ShopAddressType = {
  id?: number | null;
  shop: number;
  address: string;
  local_name: string;
};

export type MainReducerType = {
  main: {
    shops: ShopType[];
    categories: CategoryType[];
    addresses: ShopAddressType[];
  };
};
