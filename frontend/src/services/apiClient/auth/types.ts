/**
 * Response types for auth API calls to `/api/login`.
 */

/**
 * Successful payload from `POST /api/login`.
 *
 * @property {string} accessToken - JWT access token issued for the authenticated user.
 * @property {string} expiresAt - ISO-8601 timestamp when the token expires (used for cookie expiry).
 */
export type LoginResponse = {
  accessToken: string;
  expiresAt: string;
};
