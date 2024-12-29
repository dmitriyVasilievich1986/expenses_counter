import { CategoryTypeNumber } from "../categoryPage/types";

export type ShopType<C> = {
  id?: number | null;
  category: C;
  name: string;
  icon: string | null;
  description: string;
};

export type ShopTypeNumber = ShopType<number>;
export type ShopTypeDetailed = ShopType<CategoryTypeNumber>;

export type ShopAddressType<S> = {
  id?: number | null;
  shop: S;
  address: string;
  local_name: string;
  icon: string | null;
};

export type ShopAddressTypeNumber = ShopAddressType<number>;
export type ShopAddressTypeDetailed = ShopAddressType<ShopTypeNumber>;

export type ShopProps = {
  shops: ShopTypeNumber[];
  addresses: ShopAddressTypeNumber[];
};
