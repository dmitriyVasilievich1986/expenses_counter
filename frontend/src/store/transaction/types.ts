/**
 * Zustand transaction slice types: transaction entities from the API and the combined store state shape.
 */

import type { ProductSimpleType } from '../product/types';
import type { AddressType } from '../shop/types';
import type { Dayjs } from 'dayjs';

/**
 * Transaction record with nested product and address (API list/detail shape).
 *
 * @property {number} id - Transaction primary key.
 * @property {string} date - ISO date string for when the purchase occurred.
 * @property {number} count - Quantity purchased.
 * @property {number} price - Monetary value for this line item.
 * @property {number} productId - Linked product id.
 * @property {number} addressId - Linked shop address id.
 * @property {ProductSimpleType} product - Resolved product for display.
 * @property {AddressType} address - Resolved address (shop location) for display.
 */
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

/**
 * State and actions exposed by the transaction Zustand store.
 *
 * @property {Dayjs} currentDate - Calendar / filter anchor used by the transaction UI.
 * @property {(TransactionType[] | null)} transactions - Cached list; null until loaded.
 * @property {(TransactionType | null)} currentTransaction - Transaction selected for detail/edit flows.
 * @property {(date: Dayjs) => void} setCurrentDate - Updates the calendar / filter date.
 * @property {(transaction: TransactionType | null) => void} setCurrentTransaction - Sets or clears the focused transaction.
 * @property {(transactions: TransactionType[] | null) => void} setTransactions - Replaces the entire cached list.
 * @property {(transactions: TransactionType[]) => void} addTransactions - Appends transactions to the cached list.
 * @property {(transaction: TransactionType) => void} updateTransaction - Replaces one transaction in the list by id.
 * @property {(id: number) => void} deleteTransaction - Removes a transaction from the list by id.
 */
export type TransactionStoreStateType = {
  currentDate: Dayjs;
  transactions: TransactionType[] | null;
  currentTransaction: TransactionType | null;
  setCurrentDate: (date: Dayjs) => void;
  setCurrentTransaction: (transaction: TransactionType | null) => void;
  setTransactions: (transactions: TransactionType[] | null) => void;
  addTransactions: (transactions: TransactionType[]) => void;
  updateTransaction: (transaction: TransactionType) => void;
  deleteTransaction: (id: number) => void;
};
