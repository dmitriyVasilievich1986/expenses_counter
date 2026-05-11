/**
 * Request body types for transaction create and update calls to `/api/v1/transaction`.
 */

/**
 * Payload for creating a transaction (`POST /api/v1/transaction`).
 *
 * @property {string} date - Date of the transaction (ISO date string as sent in JSON).
 * @property {number} count - Quantity or amount purchased; must be non-negative on the API.
 * @property {number} price - Monetary value for this line; must be non-negative on the API.
 * @property {number} productId - Product associated with this transaction.
 * @property {number} addressId - Shop address where the transaction occurred.
 */
export type TransactionPostRequest = {
  date: string;
  count: number;
  price: number;
  productId: number;
  addressId: number;
};

/**
 * Payload for replacing a transaction (`PUT /api/v1/transaction/{id}`). Same shape as {@link TransactionPostRequest}.
 */
export type TransactionPutRequest = TransactionPostRequest;
