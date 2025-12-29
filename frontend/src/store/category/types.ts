export type CategorySimpleType = {
  id: number;
  name: string;
};

export type CategoryType = CategorySimpleType & {
  description: string | null;
  parent: CategorySimpleType | null;
};

export type CategoryStoreStateType = {
  categories: CategorySimpleType[];
  addCategories: (categories: CategorySimpleType[]) => void;
  updateCategory: (category: CategorySimpleType) => void;
  deleteCategory: (id: number) => void;
};
