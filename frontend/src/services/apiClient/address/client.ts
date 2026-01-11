import { useShopStore, type AddressType } from '@store/shop';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { AddressPostRequest, AddressPutRequest } from './types';

export const useAddressAPIClient = () => {
  const {
    addCurrentShopAddress,
    updateCurrentShopAddress,
    deleteCurrentShopAddress,
    setAddresses,
    addresses,
  } = useShopStore();
  const { wrapper } = useApiClientWrapper();

  return {
    getAddresses: async (): Promise<AddressType[]> => {
      return wrapper(async () => {
        if (addresses !== null) return addresses;
        const response = await apiClientInstance.get<{ data: AddressType[] }>(`/api/v1/address`);
        setAddresses(response.data.data);
        return response.data.data;
      });
    },
    postCurrentShopAddress: async (request: AddressPostRequest): Promise<AddressType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<AddressType>(`/api/v1/address`, request);
        addCurrentShopAddress(response.data);
        return response.data;
      });
    },
    putCurrentShopAddress: async (id: number, request: AddressPutRequest): Promise<AddressType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<AddressType>(`/api/v1/address/${id}`, request);
        updateCurrentShopAddress(response.data);
        return response.data;
      });
    },
    deleteCurrentShopAddress: async (id: number): Promise<void> => {
      return wrapper(async () => {
        await apiClientInstance.delete<void>(`/api/v1/address/${id}`);
        deleteCurrentShopAddress(id);
      });
    },
  };
};
