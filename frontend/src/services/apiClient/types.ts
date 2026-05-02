/**
 * Shared API-related type definitions used across service clients.
 */

/**
 * Pagination and sorting metadata returned with paginated list responses.
 *
 * @property {number} total - Total number of items matching the query (across all pages).
 * @property {number} offset - Number of items skipped from the start of the result set.
 * @property {number} limit - Maximum number of items returned in this page.
 * @property {string} sort_by - Field name used for ordering results.
 * @property {string} sort_order - Sort direction (e.g. ascending or descending).
 */
export type PaginationMetadata = {
  total: number;
  offset: number;
  limit: number;
  sort_by: string;
  sort_order: string;
};
