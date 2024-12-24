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

export type ProductType = {
  id?: number | null;
  name: string;
  description: string;
  sub_category: number;
};

type TransactionTypeBase = {
  id?: number | null;
  date: Date;
  price: number;
  count: number;
};

export type TransactionType = TransactionTypeBase & {
  product: number;
  address: number;
};

export type TransactionTypeDetailed = TransactionTypeBase & {
  product: ProductType;
  address: ShopAddressType;
};

export type MainReducerType = {
  main: {
    shops: ShopType[];
    products: ProductType[];
    categories: CategoryType[];
    addresses: ShopAddressType[];
    transactions: TransactionType[];
  };
};
