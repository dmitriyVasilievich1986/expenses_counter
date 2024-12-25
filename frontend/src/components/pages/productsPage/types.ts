export type ProductType<P> = {
  id?: number | null;
  name: string;
  description: string;
  sub_category: P | null;
};
