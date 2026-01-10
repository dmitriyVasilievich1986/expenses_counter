import { useShopStore, type AddressType } from '@store/shop';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { AddressPostRequest, AddressPutRequest } from './types';

export const useAddressAPIClient = () => {
  const { addAddress, updateAddress, deleteAddress } = useShopStore();
  const { wrapper } = useApiClientWrapper();

  return {
    postAddress: async (request: AddressPostRequest): Promise<AddressType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<AddressType>(`/api/v1/address`, request);
        addAddress(response.data);
        return response.data;
      });
    },
    putAddress: async (id: number, request: AddressPutRequest): Promise<AddressType> => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<AddressType>(`/api/v1/address/${id}`, request);
        updateAddress(response.data);
        return response.data;
      });
    },
    deleteAddress: async (id: number): Promise<void> => {
      return wrapper(async () => {
        await apiClientInstance.delete<void>(`/api/v1/address/${id}`);
        deleteAddress(id);
      });
    },
  };
};
