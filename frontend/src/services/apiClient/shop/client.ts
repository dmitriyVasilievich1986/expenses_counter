/**
 * Shop REST API client hook: HTTP calls to `/api/v1/shop` and syncing results into the shop store.
 */

import { useShopStore, type ShopSimpleType, type ShopType } from '@store/shop';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { ShopPostRequest, ShopPutRequest } from './types';
import type { PaginationMetadata, FilterType } from '../types';

/**
 * Plain (non-hook) fetcher for paginated shops. No store side effects — callers manage their own state.
 *
 * @returns Page payload with `data` (shops) and `total` (overall match count).
 */
export const fetchShops = async (
  limit?: number,
  offset?: number,
  sortBy?: string,
  sortOrder?: string,
  filters?: FilterType[]
): Promise<{ data: ShopSimpleType[]; total: number }> => {
  const response = await apiClientInstance.get<{
    data: ShopSimpleType[];
    metadata: PaginationMetadata;
  }>(`/api/v1/shop`, {
    params: {
      limit,
      offset,
      sortBy,
      sortOrder,
      filters: filters ? JSON.stringify(filters) : undefined,
    },
  });
  return { data: response.data.data, total: response.data.metadata.total };
};

/**
 * Hook that returns shop API functions wired to the global shop store.
 *
 * @returns Object with `getShop`, `getShops`, `postShop`, `putShop`, and `deleteShop` methods.
 */
export const useShopAPIClient = () => {
  const { addShops, setShops, setShopListLoading, updateShop, deleteShop, setCurrentShop, shops } =
    useShopStore();
  const { wrapper } = useApiClientWrapper();

  return {
    /**
     * Loads a single shop by id and sets it as the current shop in the store.
     *
     * @param {number} id - Shop primary key.
     * @returns {Promise<ShopType>} Full shop entity from the API.
     */
    getShop: async (id: number): Promise<ShopType> => {
      setShopListLoading(true);
      try {
        const response = await apiClientInstance.get<ShopType>(`/api/v1/shop/${id}`);
        setCurrentShop(response.data);
        return response.data;
      } finally {
        setShopListLoading(false);
      }
    },
    /**
     * Loads a paginated list of shops, updates the store with items and total count, and toggles list loading state.
     *
     * @param {number} [limit] - Page size passed as a query parameter.
     * @param {number} [offset] - Skip offset passed as a query parameter.
     * @param {string} [sortBy] - Field name used for ordering results.
     * @param {string} [sortOrder] - Sort direction (e.g. ascending or descending).
     * @param {FilterType[]} [filters] - Filters to apply to the query.
     * @returns {Promise<ShopSimpleType[]>} Shops for the requested page.
     */
    getShops: async (
      limit?: number,
      offset?: number,
      sortBy?: string,
      sortOrder?: string,
      filters?: FilterType[]
    ): Promise<ShopSimpleType[]> => {
      setShopListLoading(true);
      try {
        const { data, total } = await fetchShops(limit, offset, sortBy, sortOrder, filters);
        setShops(data, total);
        return data;
      } finally {
        setShopListLoading(false);
      }
    },
    /**
     * Creates a shop and appends it to the in-memory list when the list is already loaded.
     *
     * @param {ShopPostRequest} request - Payload for `POST /api/v1/shop`.
     * @returns {Promise<ShopType>} Created shop entity.
     */
    postShop: async (request: ShopPostRequest): Promise<ShopType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<ShopType>(`/api/v1/shop`, request);
        if (shops !== null) {
          addShops([response.data]);
        }
        return response.data;
      });
    },
    /**
     * Replaces a shop by id, updates it in the list when loaded, and sets it as the current shop.
     *
     * @param {number} id - Shop primary key.
     * @param {ShopPutRequest} request - Full shop payload for `PUT /api/v1/shop/{id}`.
     * @returns {Promise<ShopType>} Updated shop entity.
     */
    putShop: async (id: number, request: ShopPutRequest): Promise<ShopType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<ShopType>(`/api/v1/shop/${id}`, request);
        if (shops !== null) {
          updateShop(response.data);
        }
        setCurrentShop(response.data);
        return response.data;
      });
    },
    /**
     * Deletes a shop by id and removes it from the in-memory list when the list is loaded.
     *
     * @param {number} id - Shop primary key.
     * @returns {Promise<void>} Resolves when the delete request completes.
     */
    deleteShop: async (id: number): Promise<void> => {
      return wrapper(async () => {
        await apiClientInstance.delete<void>(`/api/v1/shop/${id}`);
        if (shops !== null) {
          deleteShop(id);
        }
      });
    },
  };
};
