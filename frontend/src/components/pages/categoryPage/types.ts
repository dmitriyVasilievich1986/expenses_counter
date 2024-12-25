export type CategoryType<C> = {
  id?: number | null;
  name: string;
  parent: C | null;
  description: string;
};
