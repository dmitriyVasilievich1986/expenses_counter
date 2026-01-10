import { useCategoryStore, type CategorySimpleType, type CategoryType } from '@store/category';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { CategoryPostRequest, CategoryPutRequest } from './types';

export const useCategoryAPIClient = () => {
  const { addCategories, updateCategory, deleteCategory, categories } = useCategoryStore();
  const { wrapper } = useApiClientWrapper();

  return {
    getCategories: async (): Promise<CategorySimpleType[]> => {
      return wrapper(async () => {
        if (categories !== null) return categories;
        const response = await apiClientInstance.get<{ data: CategorySimpleType[] }>(
          `/api/v1/category`
        );
        addCategories(response.data.data);
        return response.data.data;
      });
    },
    postCategory: async (request: CategoryPostRequest): Promise<CategoryType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<CategoryType>(`/api/v1/category`, request);
        if (categories !== null) {
          addCategories([response.data]);
        }
        return response.data;
      });
    },
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
