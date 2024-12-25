const API_URL = "/expenses/";

export enum PagesURLs {
  Category = "/create/category",
  Product = "/create/product",
  Shop = "/create/shop",
  Address = "address",
}

export enum API_URLS {
  SubCategory = `${API_URL}sub_category/`,
  Transaction = `${API_URL}transaction/`,
  Address = `${API_URL}shop_address/`,
  Category = `${API_URL}category/`,
  Product = `${API_URL}product/`,
  Shop = `${API_URL}shop/`,
}

export type APIResponseType<R> = {
  data: R;
};
