/**
 * Request body types for address create and update calls to `/api/v1/address`.
 */

/**
 * Payload for creating an address (`POST /api/v1/address`).
 *
 * @property {string} address - Full address text (e.g. street, city) as stored for the shop.
 * @property {string} localName - Human-readable label for this address within the shop.
 * @property {number} shopId - Shop the address is associated with.
 */
export type AddressPostRequest = {
  address: string;
  localName: string;
  shopId: number;
};

/**
 * Payload for replacing an address (`PUT /api/v1/address/{id}`). Same shape as {@link AddressPostRequest}.
 */
export type AddressPutRequest = AddressPostRequest;
