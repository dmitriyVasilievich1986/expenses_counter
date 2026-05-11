/**
 * Address REST API client hook: HTTP calls to `/api/v1/address` and syncing mutations into the current shop store.
 */

import { useShopStore, type AddressType } from '@store/shop';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { AddressPostRequest, AddressPutRequest } from './types';
import type { FilterType, PaginationMetadata } from '../types';

/**
 * Hook that returns address API functions wired to the current shop in the shop store.
 *
 * @returns Object with `getAddresses`, `postCurrentShopAddress`, `putCurrentShopAddress`, and `deleteCurrentShopAddress`.
 */
export const useAddressAPIClient = () => {
  const { addCurrentShopAddress, updateCurrentShopAddress, deleteCurrentShopAddress } =
    useShopStore();
  const { wrapper } = useApiClientWrapper();

  return {
    /**
     * Fetches a paginated list of addresses from the API.
     *
     * @param {number} [limit] - Page size query parameter.
     * @param {number} [offset] - Skip offset query parameter.
     * @param {string} [sortBy] - Field name used for ordering results.
     * @param {string} [sortOrder] - Sort direction (e.g. ascending or descending).
     * @param {FilterType[]} [filters] - Filters serialized into the query string when present.
     * @returns {Promise<{ data: AddressType[]; metadata: PaginationMetadata }>} Addresses and pagination metadata.
     */
    getAddresses: async (
      limit?: number,
      offset?: number,
      sortBy?: string,
      sortOrder?: string,
      filters?: FilterType[]
    ): Promise<{ data: AddressType[]; metadata: PaginationMetadata }> => {
      const response = await apiClientInstance.get<{
        data: AddressType[];
        metadata: PaginationMetadata;
      }>(`/api/v1/address`, {
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
     * Creates an address via `POST /api/v1/address` and appends it to the current shop's addresses in the store.
     *
     * @param {AddressPostRequest} request - Creation payload.
     * @returns {Promise<AddressType>} Created address entity.
     */
    postCurrentShopAddress: async (request: AddressPostRequest): Promise<AddressType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<AddressType>(`/api/v1/address`, request);
        addCurrentShopAddress(response.data);
        return response.data;
      });
    },
    /**
     * Fully replaces an address via `PUT /api/v1/address/{id}` and updates it in the current shop store.
     *
     * @param {number} id - Address primary key.
     * @param {AddressPutRequest} request - Full replacement payload.
     * @returns {Promise<AddressType>} Updated address entity.
     */
    putCurrentShopAddress: async (id: number, request: AddressPutRequest): Promise<AddressType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<AddressType>(`/api/v1/address/${id}`, request);
        updateCurrentShopAddress(response.data);
        return response.data;
      });
    },
    /**
     * Deletes an address via `DELETE /api/v1/address/{id}` and removes it from the current shop store.
     *
     * @param {number} id - Address primary key.
     * @returns {Promise<void>} Resolves when the delete request completes.
     */
    deleteCurrentShopAddress: async (id: number): Promise<void> => {
      return wrapper(async () => {
        await apiClientInstance.delete<void>(`/api/v1/address/${id}`);
        deleteCurrentShopAddress(id);
      });
    },
  };
};
