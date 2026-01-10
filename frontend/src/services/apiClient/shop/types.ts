export type ShopPostRequest = {
  name: string;
  categoryId: number;
  description: string | null;
  icon: string | null;
};

export type ShopPutRequest = ShopPostRequest;
