/**
 * Product REST API client hook: HTTP calls to `/api/v1/product` and syncing results into the product store.
 */

import { useProductStore, type ProductSimpleType, type ProductType } from '@store/product';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { ProductPostRequest, ProductPutRequest } from './types';
import type { PaginationMetadata } from '../types';

/**
 * Hook that returns product API functions wired to the global product store.
 *
 * @returns Object with `getProduct`, `getProducts`, `postProduct`, `putProduct`, and `deleteProduct` methods.
 */
export const useProductAPIClient = () => {
  const {
    setProducts,
    setProductListLoading,
    addProducts,
    updateProduct,
    deleteProduct,
    setCurrentProduct,
    products,
  } = useProductStore();
  const { wrapper } = useApiClientWrapper();

  return {
    /**
     * Loads a single product by id and sets it as the current product in the store.
     *
     * @param {number} id - Product primary key.
     * @returns {Promise<ProductType>} Full product entity from the API.
     */
    getProduct: async (id: number): Promise<ProductType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.get<ProductType>(`/api/v1/product/${id}`);
        setCurrentProduct(response.data);
        return response.data;
      });
    },
    /**
     * Loads a paginated list of products and updates the store with items and total count.
     *
     * @param {number} [limit] - Page size passed as a query parameter.
     * @param {number} [offset] - Skip offset passed as a query parameter.
     * @returns {Promise<ProductSimpleType[]>} Products for the requested page.
     */
    getProducts: async (
      limit?: number,
      offset?: number,
      sortBy?: string,
      sortOrder?: string
    ): Promise<ProductSimpleType[]> => {
      return wrapper(async () => {
        setProductListLoading(true);
        try {
          const response = await apiClientInstance.get<{
            data: ProductSimpleType[];
            metadata: PaginationMetadata;
          }>(`/api/v1/product`, {
            params: {
              limit,
              offset,
              sortBy,
              sortOrder,
            },
          });
          setProducts(response.data.data, response.data.metadata.total);
          return response.data.data;
        } finally {
          setProductListLoading(false);
        }
      });
    },
    /**
     * Creates a product and appends it to the in-memory list when the list is already loaded.
     *
     * @param {ProductPostRequest} request - Payload for `POST /api/v1/product`.
     * @returns {Promise<ProductType>} Created product entity.
     */
    postProduct: async (request: ProductPostRequest): Promise<ProductType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<ProductType>(`/api/v1/product`, request);
        if (products !== null) {
          addProducts([response.data]);
        }
        return response.data;
      });
    },
    /**
     * Replaces a product by id, sets it as the current product, and updates it in the list when loaded.
     *
     * @param {number} id - Product primary key.
     * @param {ProductPutRequest} request - Full product payload for `PUT /api/v1/product/{id}`.
     * @returns {Promise<ProductType>} Updated product entity.
     */
    putProduct: async (id: number, request: ProductPutRequest): Promise<ProductType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<ProductType>(`/api/v1/product/${id}`, request);
        setCurrentProduct(response.data);
        if (products !== null) {
          updateProduct(response.data);
        }
        return response.data;
      });
    },
    /**
     * Deletes a product by id and removes it from the in-memory list when the list is loaded.
     *
     * @param {number} id - Product primary key.
     * @returns {Promise<void>} Resolves when the delete request completes.
     */
    deleteProduct: async (id: number): Promise<void> => {
      return wrapper(async () => {
        await apiClientInstance.delete<void>(`/api/v1/product/${id}`);
        if (products !== null) {
          deleteProduct(id);
        }
      });
    },
  };
};
