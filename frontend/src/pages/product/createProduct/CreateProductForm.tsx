import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import { useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router';

import { AsyncInput } from '@components/asyncInput';
import { Input } from '@components/input';
import { SubmitButton } from '@components/submitButton';
import { useProductAPIClient } from '@services/apiClient/product/client';
import type { ProductPostRequest } from '@services/apiClient/product/types';
import type { CategorySimpleType } from '@store/category';
import { useMainStore } from '@store/main';
import { useProductStore } from '@store/product';
import { useCategoryAPIClient } from '@services/apiClient';
import { useCategoryStore } from '@store/category';

export function CreateProductForm() {
  const navigate = useNavigate();
  const { productId } = useParams();
  const formRef = useRef<HTMLFormElement>(null);
  const { getCategories } = useCategoryAPIClient();
  const { categories } = useCategoryStore();

  const currentProduct = useProductStore((state) => state.currentProduct);
  const [category, setCategory] = useState<CategorySimpleType | null>(
    currentProduct?.category ?? null
  );

  const { postProduct, putProduct } = useProductAPIClient();

  const isLoading = useMainStore((state) => state.isLoading);

  const clickHandler = async () => {
    const formData = new FormData(formRef.current as HTMLFormElement);
    const data = Object.fromEntries(formData.entries()) as unknown as ProductPostRequest;
    data.categoryId = category!.id;

    if (productId === undefined) {
      try {
        const response = await postProduct(data);
        navigate(`/product/${response.id}`);
      } catch (error) {
        console.error(error);
      }
    } else {
      await putProduct(parseInt(productId), data);
    }
  };

  return (
    <form style={{ marginTop: '1rem' }} ref={formRef} onSubmit={(e) => e.preventDefault()}>
      <Stack direction="column" spacing={2}>
        <Input label="Product name" name="name" defaultValue={currentProduct?.name ?? ''} />
        <Input
          label="Product description"
          name="description"
          defaultValue={currentProduct?.description ?? ''}
        />
        <AsyncInput
          value={category}
          onChange={setCategory}
          items={categories}
          getItems={getCategories}
          label="Category"
        />
      </Stack>
      <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
        <SubmitButton
          disabled={isLoading}
          variant={!productId ? 'create' : 'update'}
          onClick={clickHandler}
        />
      </Box>
    </form>
  );
}
