/**
 * Public entry for the product API client: re-exports {@link fetchProducts}, {@link useProductAPIClient},
 * and request payload types used by callers.
 *
 * @module services/apiClient/product
 */

import { fetchProducts, useProductAPIClient } from './client';

import type { ProductPostRequest, ProductPutRequest } from './types';

export { fetchProducts, useProductAPIClient, type ProductPostRequest, type ProductPutRequest };
