import { useProductStore, type ProductSimpleType, type ProductType } from '@store/product';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { ProductPostRequest, ProductPutRequest } from './types';

export const useProductAPIClient = () => {
  const { addProducts, updateProduct, deleteProduct, setCurrentProduct, products } =
    useProductStore();
  const { wrapper } = useApiClientWrapper();

  return {
    getProduct: async (id: number): Promise<ProductType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.get<ProductType>(`/api/v1/product/${id}`);
        setCurrentProduct(response.data);
        return response.data;
      });
    },
    getProducts: async (): Promise<ProductSimpleType[]> => {
      return wrapper(async () => {
        if (products !== null) return products;
        const response = await apiClientInstance.get<{ data: ProductSimpleType[] }>(
          `/api/v1/product`
        );
        addProducts(response.data.data);
        return response.data.data;
      });
    },
    postProduct: async (request: ProductPostRequest): Promise<ProductType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<ProductType>(`/api/v1/product`, request);
        if (products !== null) {
          addProducts([response.data]);
        }
        return response.data;
      });
    },
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
