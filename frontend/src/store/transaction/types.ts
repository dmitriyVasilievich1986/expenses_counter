import type { ProductSimpleType } from '../product/types';
import type { AddressType } from '../shop/types';
import type { Dayjs } from 'dayjs';

export type TransactionType = {
  id: number;
  date: string;
  count: number;
  price: number;
  productId: number;
  addressId: number;
  product: ProductSimpleType;
  address: AddressType;
};

export type TransactionStoreStateType = {
  currentDate: Dayjs;
  transactions: TransactionType[] | null;
  currentTransaction: TransactionType | null;
  setCurrentDate: (date: Dayjs) => void;
  setCurrentTransaction: (transaction: TransactionType | null) => void;
  setTransactions: (transactions: TransactionType[]) => void;
  addTransactions: (transactions: TransactionType[]) => void;
  updateTransaction: (transaction: TransactionType) => void;
  deleteTransaction: (id: number) => void;
};
