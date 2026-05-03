/**
 * Barrel module for the shop Zustand store: re-exports {@link useShopStore} and public entity types from `./types`.
 */

import { useShopStore } from './shopStore';

import type { AddressType, ShopSimpleType, ShopType } from './types';

export { useShopStore, type ShopSimpleType, type ShopType, type AddressType };
