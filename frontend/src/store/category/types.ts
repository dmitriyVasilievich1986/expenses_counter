/**
 * Zustand category slice types: entities used in the UI and the combined store state shape.
 */

/**
 * Category fields used in lists and as nested references (minimal shape).
 *
 * @property {number} id - Category primary key.
 * @property {string} name - Display name.
 */
export type CategorySimpleType = {
  id: number;
  name: string;
};

/**
 * Full category entity with optional description and parent link (e.g. detail or tree views).
 *
 * @property {(string | null)} description - Optional longer text, or null when absent.
 * @property {(CategorySimpleType | null)} parent - Parent category when this is a subcategory, or null for a root.
 */
export type CategoryType = CategorySimpleType & {
  description: string | null;
  parent: CategorySimpleType | null;
};

/**
 * State and actions exposed by the category Zustand store.
 *
 * @property {(CategorySimpleType[] | null)} categories - Cached list; null until loaded.
 * @property {(categories: CategorySimpleType[]) => void} setCategories - Replaces the entire cached list.
 * @property {(categories: CategorySimpleType[]) => void} addCategories - Appends categories to the cached list.
 * @property {(category: CategorySimpleType) => void} updateCategory - Replaces one category in the list by id.
 * @property {(id: number) => void} deleteCategory - Removes a category from the list by id.
 */
export type CategoryStoreStateType = {
  categories: CategorySimpleType[] | null;
  addCategories: (categories: CategorySimpleType[]) => void;
  setCategories: (categories: CategorySimpleType[]) => void;
  updateCategory: (category: CategorySimpleType) => void;
  deleteCategory: (id: number) => void;
};
