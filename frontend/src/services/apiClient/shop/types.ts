/**
 * Request body types for shop create and update calls to `/api/v1/shop`.
 */

/**
 * Payload for creating a shop (`POST /api/v1/shop`).
 *
 * @property {string} name - Display name of the shop.
 * @property {number} categoryId - Category the shop belongs to.
 * @property {(string | null)} description - Optional longer description, or null when absent.
 * @property {(string | null)} icon - Optional icon URL or identifier, or null when absent.
 */
export type ShopPostRequest = {
  name: string;
  categoryId: number;
  description: string | null;
  icon: string | null;
};

/**
 * Payload for replacing a shop (`PUT /api/v1/shop/{id}`). Same shape as {@link ShopPostRequest}.
 */
export type ShopPutRequest = ShopPostRequest;
