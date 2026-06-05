/**
 * Response types for statistics endpoints under `/api/v1/statistics`.
 */

/**
 * Monthly spending total returned by `GET /api/v1/statistics/spendings/grouped-by-month`.
 *
 * @property {string} month - First day of the month as an ISO date string (e.g. `YYYY-MM-01`).
 * @property {number} spendings - Total amount spent in that month for the authenticated user.
 */
export type SpendingsGroupedByMonthResponse = {
  month: string;
  spendings: number;
};

/**
 * Product price entry returned by `POST /api/v1/statistics/product-price`.
 *
 * @property {number} productId - Product the price belongs to.
 * @property {number} price - Transaction price recorded for this product.
 * @property {string} date - Date of the transaction as an ISO date string.
 */
export type ProductPriceResponse = {
  productId: number;
  price: number;
  date: string;
};
