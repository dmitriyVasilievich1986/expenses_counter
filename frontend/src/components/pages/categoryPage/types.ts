export type CategoryType<C> = {
  id?: number | null;
  name: string;
  parent: C | null;
  description: string;
};

export type CategoryTypeNumber = CategoryType<number>;
export type CategoryTypeDetailed = CategoryType<CategoryTypeNumber>;
