/**
 * Public entry for the statistics API client: re-exports {@link useStatisticsAPIClient}.
 *
 * @module services/apiClient/statistics/index
 */

export type { SpendingsGroupedByMonthResponse, ProductPriceResponse } from './types';
export { useStatisticsAPIClient } from './client';
