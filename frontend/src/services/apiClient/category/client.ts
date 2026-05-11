/**
 * Category REST API client hook: HTTP calls to `/api/v1/category` and syncing mutations into the category store when a list is already loaded.
 */

import { useCategoryStore, type CategorySimpleType, type CategoryType } from '@store/category';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { CategoryPostRequest, CategoryPutRequest } from './types';
import type { FilterType, PaginationMetadata } from '../types';

/**
 * Hook that returns category API functions wired to the global category store.
 *
 * @returns Object with `getCategories`, `postCategory`, `putCategory`, and `deleteCategory` methods.
 */
export const useCategoryAPIClient = () => {
  const { addCategories, updateCategory, deleteCategory, categories } = useCategoryStore();
  const { wrapper } = useApiClientWrapper();

  return {
    /**
     * Fetches a paginated list of categories from the API.
     *
     * @param {number} [limit] - Page size query parameter.
     * @param {number} [offset] - Skip offset query parameter.
     * @param {string} [sortBy] - Field name used for ordering results.
     * @param {string} [sortOrder] - Sort direction (e.g. ascending or descending).
     * @param {FilterType[]} [filters] - Filters serialized into the query string when present.
     * @returns {Promise<{ data: CategorySimpleType[]; metadata: PaginationMetadata }>} Categories and pagination metadata.
     */
    getCategories: async (
      limit?: number,
      offset?: number,
      sortBy?: string,
      sortOrder?: string,
      filters?: FilterType[]
    ): Promise<{ data: CategorySimpleType[]; metadata: PaginationMetadata }> => {
      const response = await apiClientInstance.get<{
        data: CategorySimpleType[];
        metadata: PaginationMetadata;
      }>(`/api/v1/category`, {
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
     * Creates a category via `POST /api/v1/category` and appends it to the in-memory list when categories are already loaded.
     *
     * @param {CategoryPostRequest} request - Creation payload.
     * @returns {Promise<CategoryType>} Created category entity.
     */
    postCategory: async (request: CategoryPostRequest): Promise<CategoryType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<CategoryType>(`/api/v1/category`, request);
        if (categories !== null) {
          addCategories([response.data]);
        }
        return response.data;
      });
    },
    /**
     * Replaces a category via `PUT /api/v1/category/{id}` and updates it in the in-memory list when categories are loaded.
     *
     * @param {number} id - Category primary key.
     * @param {CategoryPutRequest} request - Full replacement payload.
     * @returns {Promise<CategoryType>} Updated category entity.
     */
    putCategory: async (id: number, request: CategoryPutRequest): Promise<CategoryType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<CategoryType>(
          `/api/v1/category/${id}`,
          request
        );
        if (categories !== null) {
          updateCategory(response.data);
        }
        return response.data;
      });
    },
    /**
     * Deletes a category via `DELETE /api/v1/category/{id}` and removes it from the in-memory list when categories are loaded.
     *
     * @param {number} id - Category primary key.
     * @returns {Promise<void>} Resolves when the delete request completes.
     */
    deleteCategory: async (id: number): Promise<void> => {
      return wrapper(async () => {
        await apiClientInstance.delete<void>(`/api/v1/category/${id}`);
        if (categories !== null) {
          deleteCategory(id);
        }
      });
    },
  };
};
