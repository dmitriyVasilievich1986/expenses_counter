export type ProductType<C> = {
  id?: number | null;
  name: string;
  description: string;
  sub_category: C | null;
};
