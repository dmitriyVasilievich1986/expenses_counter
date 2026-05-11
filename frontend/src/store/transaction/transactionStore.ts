/**
 * Zustand store for transactions: list (`null` until loaded), calendar date selection, and the transaction in focus.
 *
 * Wrapped with Redux DevTools middleware for debugging.
 */

import dayjs from 'dayjs';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { TransactionType, TransactionStoreStateType } from './types';

/** Hook returning transaction store state and actions (see {@link TransactionStoreStateType}). */
export const useTransactionStore = create<TransactionStoreStateType>()(
  devtools((set) => ({
    transactions: null,
    currentDate: dayjs(),
    currentTransaction: null,
    setCurrentDate: (date) => set({ currentDate: date }, undefined, 'setCurrentDate'),
    setCurrentTransaction: (transaction) =>
      set({ currentTransaction: transaction }, undefined, 'setCurrentTransaction'),
    setTransactions: (transactions) =>
      set({ transactions: transactions }, undefined, 'setTransactions'),
    addTransactions: (transactions) =>
      set(
        (state) => ({ transactions: [...(state.transactions ?? []), ...transactions] }),
        undefined,
        'addTransactions'
      ),
    updateTransaction: (transaction) =>
      set(
        (state) => {
          return {
            transactions: (state.transactions as TransactionType[]).map((t) =>
              t.id === transaction.id ? transaction : t
            ),
          };
        },
        undefined,
        'updateTransaction'
      ),
    deleteTransaction: (id) =>
      set(
        (state) => {
          return {
            transactions: (state.transactions as TransactionType[]).filter((t) => t.id !== id),
          };
        },
        undefined,
        'deleteTransaction'
      ),
  }))
);
