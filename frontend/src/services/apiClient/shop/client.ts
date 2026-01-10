import { useShopStore, type ShopSimpleType, type ShopType } from '@store/shop';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { ShopPostRequest, ShopPutRequest } from './types';

export const useShopAPIClient = () => {
  const { addShops, updateShop, deleteShop, setCurrentShop, shops } = useShopStore();
  const { wrapper } = useApiClientWrapper();

  return {
    getShop: async (id: number): Promise<ShopType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.get<ShopType>(`/api/v1/shop/${id}`);
        setCurrentShop(response.data);
        return response.data;
      });
    },
    getShops: async (): Promise<ShopSimpleType[]> => {
      return wrapper(async () => {
        if (shops !== null) return shops;
        const response = await apiClientInstance.get<{ data: ShopSimpleType[] }>(`/api/v1/shop`);
        addShops(response.data.data);
        return response.data.data;
      });
    },
    postShop: async (request: ShopPostRequest): Promise<ShopType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<ShopType>(`/api/v1/shop`, request);
        if (shops !== null) {
          addShops([response.data]);
        }
        return response.data;
      });
    },
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
