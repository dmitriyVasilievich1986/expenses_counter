const API_URL = "/expenses/";

export enum PagesURLs {
  Transaction = "/create/transaction",
  Category = "/create/category",
  Product = "/create/product",
  Shop = "/create/shop",
  Address = "address",
}

export enum API_URLS {
  TransactionDateRange = `${API_URL}transaction/date_range/`,
  ProductPopular = `${API_URL}product/popular/`,
  ProductPrice = `${API_URL}product/price/`,
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
