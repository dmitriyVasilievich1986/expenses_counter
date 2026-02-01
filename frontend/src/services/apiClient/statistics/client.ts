import type { ProductSimpleType } from '@store/product/types';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { SpendingsGroupedByMonthResponse } from './types';

export const useStatisticsAPIClient = () => {
  const { wrapper } = useApiClientWrapper();

  return {
    getSpendingsGroupedByMonth: async (): Promise<SpendingsGroupedByMonthResponse[]> => {
      return wrapper(async () => {
        const response = await apiClientInstance.get<SpendingsGroupedByMonthResponse[]>(
          '/api/v1/statistics/spendings/grouped-by-month'
        );
        return response.data;
      });
    },
    getMostPopularProducts: async (limit: number = 10): Promise<ProductSimpleType[]> => {
      return wrapper(async () => {
        const response = await apiClientInstance.get<ProductSimpleType[]>(
          '/api/v1/statistics/most-popular-products',
          { params: { limit } }
        );
        return response.data;
      });
    },
  };
};
