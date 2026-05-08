/**
 * Zustand shop slice types: entities returned from the API and the combined store state shape.
 */

import type { CategorySimpleType } from '../category/types';

/**
 * Physical location linked to a shop.
 *
 * @property {number} id - Address primary key.
 * @property {string} address - Street or formatted address line.
 * @property {string} localName - Human-friendly label for this location.
 */
export type AddressType = {
  id: number;
  address: string;
  localName: string;
};

/**
 * Shop fields used in list views and lightweight responses (no nested relations).
 *
 * @property {number} id - Shop primary key.
 * @property {string} name - Display name.
 * @property {(string | null)} description - Optional description text.
 * @property {(string | null)} icon - Optional icon URL or identifier.
 * @property {(number | null)} categoryId - Owning category id when known.
 */
export type ShopSimpleType = {
  id: number;
  name: string;
  description: string | null;
  icon: string | null;
  categoryId: number | null;
};

/**
 * Full shop entity with nested category and addresses (e.g. detail view).
 *
 * @property {CategorySimpleType} category - Resolved category for this shop.
 * @property {AddressType[]} addresses - Locations belonging to this shop.
 */
export type ShopType = ShopSimpleType & {
  category: CategorySimpleType;
  addresses: AddressType[];
};

/**
 * State and actions exposed by the shop Zustand store.
 *
 * @property {(ShopType | null)} currentShop - Shop selected for detail/edit flows.
 * @property {(ShopSimpleType[] | null)} shops - Cached list page; null until loaded.
 * @property {(AddressType[] | null)} addresses - Optional address list cache; when non-null, address helpers update it together with the current shop's nested addresses.
 * @property {(shops: ShopSimpleType[]) => void} addShops - Appends shops to the cached list.
 * @property {(shops: ShopSimpleType[]) => void} setShops - Replaces the list and total count.
 * @property {(shop: ShopSimpleType) => void} updateShop - Merges one shop into the cached list by id.
 * @property {(id: number) => void} deleteShop - Removes a shop from the cached list by id.
 * @property {(shop: ShopType | null) => void} setCurrentShop - Sets or clears the detail shop.
 * @property {(address: AddressType) => void} addCurrentShopAddress - Appends an address on the current shop.
 * @property {(address: AddressType) => void} updateCurrentShopAddress - Replaces an address on the current shop by id.
 * @property {(id: number) => void} deleteCurrentShopAddress - Removes an address from the current shop by id.
 * @property {(addresses: AddressType[]) => void} setAddresses - Replaces the standalone addresses cache.
 */
export type ShopStoreStateType = {
  currentShop: ShopType | null;
  shops: ShopSimpleType[] | null;
  addresses: AddressType[] | null;
  addShops: (shops: ShopSimpleType[]) => void;
  setShops: (shops: ShopSimpleType[]) => void;
  updateShop: (shop: ShopSimpleType) => void;
  deleteShop: (id: number) => void;
  setCurrentShop: (shop: ShopType | null) => void;
  addCurrentShopAddress: (address: AddressType) => void;
  updateCurrentShopAddress: (address: AddressType) => void;
  deleteCurrentShopAddress: (id: number) => void;
  setAddresses: (addresses: AddressType[]) => void;
};
