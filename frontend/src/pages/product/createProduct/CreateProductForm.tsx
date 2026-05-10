/**
 * Product name/description and category form: creates a new product or updates the current one from the route,
 * using `currentProduct` from the store for defaults when editing.
 *
 * @module pages/product/createProduct/CreateProductForm
 */

import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import { useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router';

import { AsyncInput } from '@components/asyncInput';
import { Input } from '@components/input';
import { SubmitButton } from '@components/submitButton';
import { useCategoryAPIClient } from '@services/apiClient';
import { useProductAPIClient } from '@services/apiClient/product/client';
import type { ProductPostRequest } from '@services/apiClient/product/types';
import type { CategorySimpleType } from '@store/category';
import { useCategoryStore } from '@store/category';
import { useProductStore } from '@store/product';

/**
 * Renders the product fields, category picker, and a submit button wired to POST or PUT via the product API.
 *
 * @returns The product create/update form.
 */
export function CreateProductForm() {
  const formRef = useRef<HTMLFormElement>(null);

  const navigate = useNavigate();
  const { productId } = useParams();

  const { getCategories } = useCategoryAPIClient();
  const { postProduct, putProduct } = useProductAPIClient();

  const currentProduct = useProductStore((state) => state.currentProduct);
  const { categories, setCategories } = useCategoryStore();

  const [category, setCategory] = useState<CategorySimpleType | null>(
    currentProduct?.category ?? null
  );

  /** Creates a product and navigates to its page, or updates the product identified by `productId`. */
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
          setItems={setCategories}
          label="Category"
        />
      </Stack>
      <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
        <SubmitButton
          label={!productId ? 'Create' : 'Update'}
          color={!productId ? 'primary' : 'secondary'}
          onClick={clickHandler}
        />
      </Box>
    </form>
  );
}
