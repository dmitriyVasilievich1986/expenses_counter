/**
 * Type definitions for `CardsStack` list items.
 */

/**
 * Fields required to render an item as a card in the stack grid.
 *
 * @property {number} id - Unique key for list rendering and identity.
 * @property {string} name - Primary label shown on the card.
 * @property {(string | null)} [description] - Optional secondary text.
 * @property {(string | null)} [icon] - Optional icon identifier or URL.
 */
export type ItemType = {
  id: number;
  name: string;
  description?: string | null;
  icon?: string | null;
};
