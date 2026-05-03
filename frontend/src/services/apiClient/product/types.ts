/**
 * Request body types for product create and update calls to `/api/v1/product`.
 */

/**
 * Payload for creating a product (`POST /api/v1/product`).
 *
 * @property {string} name - Display name of the product.
 * @property {number} categoryId - Category (subcategory) the product belongs to.
 * @property {(string | null)} description - Optional longer description, or null when absent.
 */
export type ProductPostRequest = {
  name: string;
  categoryId: number;
  description: string | null;
};

/**
 * Payload for replacing a product (`PUT /api/v1/product/{id}`). Same shape as {@link ProductPostRequest}.
 */
export type ProductPutRequest = ProductPostRequest;
