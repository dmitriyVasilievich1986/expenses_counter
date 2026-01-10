export type ProductPostRequest = {
  name: string;
  categoryId: number;
  description: string | null;
};

export type ProductPutRequest = ProductPostRequest;
