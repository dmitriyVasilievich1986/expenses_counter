export type TransactionPostRequest = {
  date: string;
  count: number;
  price: number;
  productId: number;
  addressId: number;
};

export type TransactionPutRequest = TransactionPostRequest;
