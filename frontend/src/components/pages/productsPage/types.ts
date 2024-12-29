import { CategoryTypeNumber } from "../categoryPage/types";

export type ProductType<C> = {
  id?: number | null;
  name: string;
  sub_category: C;
  description: string;
};

export type ProductTypeNumber = ProductType<number>;
export type ProductTypeDetailed = ProductType<CategoryTypeNumber>;
