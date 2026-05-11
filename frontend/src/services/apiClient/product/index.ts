/**
 * Public entry for the product API client: re-exports {@link useProductAPIClient},
 * and request payload types used by callers.
 *
 * @module services/apiClient/product
 */

import { useProductAPIClient } from './client';

import type { ProductPostRequest, ProductPutRequest } from './types';

export { useProductAPIClient, type ProductPostRequest, type ProductPutRequest };
