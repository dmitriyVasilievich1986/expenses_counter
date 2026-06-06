/**
 * Statistics REST API client hook: HTTP calls to `/api/v1/statistics` for spending and product analytics.
 */

import type { ProductSimpleType } from '@store/product/types';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { SpendingsGroupedByMonthResponse, ProductPriceResponse } from './types';

/**
 * Hook that returns statistics API functions wrapped with the global loading handler.
 *
 * @returns Object with `getSpendingsGroupedByMonth`, `getMostPopularProducts`, and `getProductPrice` methods.
 */
export const useStatisticsAPIClient = () => {
  const { wrapper } = useApiClientWrapper();

  return {
    /**
     * Fetches the authenticated user's total spendings grouped by month from
     * `GET /api/v1/statistics/spendings/grouped-by-month`.
     *
     * @returns {Promise<SpendingsGroupedByMonthResponse[]>} Monthly spending totals, one entry per month.
     */
    getSpendingsGroupedByMonth: async (): Promise<SpendingsGroupedByMonthResponse[]> => {
      return wrapper(async () => {
        const response = await apiClientInstance.get<SpendingsGroupedByMonthResponse[]>(
          '/api/v1/statistics/spendings/grouped-by-month'
        );
        return response.data;
      });
    },
    /**
     * Fetches the most frequently purchased products for the authenticated user from
     * `GET /api/v1/statistics/most-popular-products`.
     *
     * @param {number} [limit=10] - Maximum number of products to return.
     * @returns {Promise<ProductSimpleType[]>} Products ordered by purchase frequency.
     */
    getMostPopularProducts: async (limit: number = 10): Promise<ProductSimpleType[]> => {
      return wrapper(async () => {
        const response = await apiClientInstance.get<ProductSimpleType[]>(
          '/api/v1/statistics/most-popular-products',
          { params: { limit } }
        );
        return response.data;
      });
    },
    /**
     * Fetches transaction prices for the given products from `POST /api/v1/statistics/product-price`.
     *
     * @param {number[]} productIds - Product primary keys to look up prices for.
     * @returns {Promise<ProductPriceResponse[]>} Price entries for matching transactions.
     */
    getProductPrice: async (productIds: number[]): Promise<ProductPriceResponse[]> => {
      return wrapper(async () => {
        const response = await apiClientInstance.post<ProductPriceResponse[]>(
          '/api/v1/statistics/product-price',
          { productIds }
        );
        return response.data;
      });
    },
  };
};
