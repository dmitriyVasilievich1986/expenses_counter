/**
 * Transaction REST API client hook: HTTP calls to `/api/v1/transaction` and syncing mutations into the transaction store.
 */

import { useTransactionStore, type TransactionType } from '@store/transaction';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { TransactionPostRequest, TransactionPutRequest } from './types';
import type { FilterType, PaginationMetadata } from '../types';

/**
 * Hook that returns transaction API functions wired to the global transaction store.
 *
 * @returns Object with `getTransaction`, `getTransactions`, `postTransaction`, `putTransaction`, and `deleteTransaction` methods.
 */
export const useTransactionAPIClient = () => {
  const { addTransactions, updateTransaction, deleteTransaction, setCurrentTransaction } =
    useTransactionStore();
  const { wrapper } = useApiClientWrapper();

  return {
    /**
     * Fetches a single transaction by id from `GET /api/v1/transaction/{id}`.
     *
     * @param {number} id - Transaction primary key.
     * @returns {Promise<TransactionType>} Transaction entity.
     */
    getTransaction: async (id: number): Promise<TransactionType> => {
      const response = await apiClientInstance.get<TransactionType>(`/api/v1/transaction/${id}`);
      return response.data;
    },
    /**
     * Fetches a paginated list of transactions from `GET /api/v1/transaction`.
     *
     * @param {number} [limit] - Page size query parameter.
     * @param {number} [offset] - Skip offset query parameter.
     * @param {string} [sortBy] - Field name used for ordering results.
     * @param {string} [sortOrder] - Sort direction (e.g. ascending or descending).
     * @param {FilterType[]} [filters] - Filters serialized into the query string when present.
     * @returns {Promise<{ data: TransactionType[]; metadata: PaginationMetadata }>} Transactions and pagination metadata.
     */
    getTransactions: async (
      limit?: number,
      offset?: number,
      sortBy?: string,
      sortOrder?: string,
      filters?: FilterType[]
    ): Promise<{ data: TransactionType[]; metadata: PaginationMetadata }> => {
      const response = await apiClientInstance.get<{
        data: TransactionType[];
        metadata: PaginationMetadata;
      }>('/api/v1/transaction', {
        params: {
          limit,
          offset,
          sortBy,
          sortOrder,
          filters: filters ? JSON.stringify(filters) : undefined,
        },
      });
      return response.data;
    },
    /**
     * Creates a transaction via `POST /api/v1/transaction` and appends the created row to the store list.
     *
     * @param {TransactionPostRequest} request - Creation payload.
     * @returns {Promise<TransactionType>} Created transaction entity.
     */
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
    /**
     * Replaces a transaction via `PUT /api/v1/transaction/{id}`, updates the focused transaction in the store, and merges it into the list by id.
     *
     * @param {number} id - Transaction primary key.
     * @param {TransactionPutRequest} request - Full replacement payload.
     * @returns {Promise<TransactionType>} Updated transaction entity.
     */
    putTransaction: async (
      id: number,
      request: TransactionPutRequest
    ): Promise<TransactionType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<TransactionType>(
          `/api/v1/transaction/${id}`,
          request
        );
        setCurrentTransaction(response.data);
        updateTransaction(response.data);
        return response.data;
      });
    },
    /**
     * Deletes a transaction via `DELETE /api/v1/transaction/{id}` and removes it from the in-memory list.
     *
     * @param {number} id - Transaction primary key.
     * @returns {Promise<void>} Resolves when the delete request completes.
     */
    deleteTransaction: async (id: number): Promise<void> => {
      return wrapper(async () => {
        await apiClientInstance.delete<void>(`/api/v1/transaction/${id}`);
        deleteTransaction(id);
      });
    },
  };
};
