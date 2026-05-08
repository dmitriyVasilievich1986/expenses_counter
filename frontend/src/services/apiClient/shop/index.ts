/**
 * Barrel module for the shop API client: re-exports {@link useShopAPIClient} from `./client`.
 */

import { fetchShops, useShopAPIClient } from './client';

export { fetchShops, useShopAPIClient };
