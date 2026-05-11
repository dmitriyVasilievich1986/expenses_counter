/**
 * Request body types for category create and update calls to `/api/v1/category`.
 */

/**
 * Payload for creating a category (`POST /api/v1/category`).
 *
 * @property {string} name - Display name of the category (required, non-empty on the API).
 * @property {(string | null)} description - Optional longer description, or null when absent.
 * @property {(number | null)} parentId - Parent category id for a subcategory, or null for a root category.
 */
export type CategoryPostRequest = {
  name: string;
  description: string | null;
  parentId: number | null;
};

/**
 * Payload for replacing a category (`PUT /api/v1/category/{id}`). Same shape as {@link CategoryPostRequest}.
 */
export type CategoryPutRequest = CategoryPostRequest;
