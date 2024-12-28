import { CategoryTypeNumber } from "../categoryPage/types";

export type ProductType<C> = {
  id?: number | null;
  name: string;
  description: string;
  sub_category: C | null;
};

export type ProductTypeNumber = ProductType<number>;
export type ProductTypeDetailed = ProductType<CategoryTypeNumber>;
