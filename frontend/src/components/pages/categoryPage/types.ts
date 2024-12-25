type CategoryTypeBase = {
  id?: number | null;
  name: string;
  description: string;
};

export type CategoryType = CategoryTypeBase & {
  parent: number | null;
};

export type CategoryTypeDetailed = CategoryTypeBase & {
  parent: CategoryType | null;
};
