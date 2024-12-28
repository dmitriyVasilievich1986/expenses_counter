import { ProductTypeNumber, ProductTypeDetailed } from "../productsPage/types";
import { ShopAddressTypeNumber } from "../shopsPage/types";

export type TransactionType<P, A> = {
  id?: number | null;
  date: Date;
  price: number;
  count: number;
  product: P;
  address: A;
};

export type TransactionTypeNumber = TransactionType<
  ProductTypeNumber,
  ShopAddressTypeNumber
>;
export type TransactionTypeDetailed = TransactionType<
  ProductTypeDetailed,
  ShopAddressTypeNumber
>;
