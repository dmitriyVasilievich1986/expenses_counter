import { useTransactionStore, type TransactionType } from '@store/transaction';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { TransactionPostRequest, TransactionPutRequest } from './types';
import type { Dayjs } from 'dayjs';

export const useTransactionAPIClient = () => {
  const {
    addTransactions,
    setTransactions,
    updateTransaction,
    deleteTransaction,
    setCurrentTransaction,
  } = useTransactionStore();
  const { wrapper } = useApiClientWrapper();

  return {
    getTransaction: async (id: number): Promise<TransactionType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.get<TransactionType>(`/api/v1/transaction/${id}`);
        setCurrentTransaction(response.data);
        return response.data;
      });
    },
    getTransactions: async (date: Dayjs): Promise<TransactionType[]> => {
      return wrapper(async () => {
        const data = { date: date.format('YYYY-MM-DD') };
        const response = await apiClientInstance.post<{ data: TransactionType[] }>(
          `/api/v1/transaction/monthly`,
          data
        );
        setTransactions(response.data.data);
        return response.data.data;
      });
    },
    postTransaction: async (request: TransactionPostRequest): Promise<TransactionType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<TransactionType>(
          `/api/v1/transaction`,
          request
        );
        addTransactions([response.data]);
        return response.data;
      });
    },
    putTransaction: async (
      id: number,
      request: TransactionPutRequest
    ): Promise<TransactionType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<TransactionType>(
          `/api/v1/transaction/${id}`,
          request
        );
        updateTransaction(response.data);
        return response.data;
      });
    },
    deleteTransaction: async (id: number): Promise<void> => {
      return wrapper(async () => {
        await apiClientInstance.delete<void>(`/api/v1/transaction/${id}`);
        deleteTransaction(id);
      });
    },
  };
};
