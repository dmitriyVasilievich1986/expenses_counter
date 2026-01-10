export type CategoryPostRequest = {
  name: string;
  description: string | null;
  parentId: number | null;
};

export type CategoryPutRequest = CategoryPostRequest;
