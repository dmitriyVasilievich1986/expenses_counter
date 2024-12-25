export type TransactionType<P, A> = {
  id?: number | null;
  date: Date;
  price: number;
  count: number;
  product: P;
  address: A;
};
