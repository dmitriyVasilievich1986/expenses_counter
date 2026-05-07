/**
 * Shop name/description/icon and category form: creates a new shop or updates the current one from the route,
 * using `currentShop` from the store for defaults when editing.
 *
 * @module pages/shop/createShop/CreateShopForm
 */

import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import { useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router';

import { AsyncInput } from '@components/asyncInput';
import { Input } from '@components/input';
import { SubmitButton } from '@components/submitButton';
import { useShopAPIClient, useCategoryAPIClient } from '@services/apiClient';
import type { ShopPostRequest } from '@services/apiClient/shop/types';
import type { CategorySimpleType } from '@store/category';
import { useCategoryStore } from '@store/category';
import { useMainStore } from '@store/main';
import { useShopStore } from '@store/shop';

/**
 * Renders the shop fields, category picker, and a submit button wired to POST or PUT via the shop API.
 *
 * @returns The shop create/update form.
 */
export function CreateShopForm() {
  const navigate = useNavigate();
  const { shopId } = useParams();
  const formRef = useRef<HTMLFormElement>(null);
  const { getCategories } = useCategoryAPIClient();
  const { categories } = useCategoryStore();

  const currentShop = useShopStore((state) => state.currentShop);
  const [category, setCategory] = useState<CategorySimpleType | null>(
    currentShop?.category ?? null
  );

  const { postShop, putShop } = useShopAPIClient();

  const isLoading = useMainStore((state) => state.isLoading);

  /** Creates a shop and navigates to its page, or updates the shop identified by `shopId`. */
  const clickHandler = async () => {
    const formData = new FormData(formRef.current as HTMLFormElement);
    const data = Object.fromEntries(formData.entries()) as unknown as ShopPostRequest;
    data.categoryId = category!.id;

    if (shopId === undefined) {
      try {
        const response = await postShop(data);
        navigate(`/shop/${response.id}`);
      } catch (error) {
        console.error(error);
      }
    } else {
      await putShop(parseInt(shopId), data);
    }
  };

  return (
    <form style={{ marginTop: '1rem' }} ref={formRef} onSubmit={(e) => e.preventDefault()}>
      <Stack direction="column" spacing={2}>
        <Input label="Shop name" name="name" defaultValue={currentShop?.name ?? ''} />
        <Input
          label="Shop description"
          name="description"
          defaultValue={currentShop?.description ?? ''}
        />
        <Input label="Shop logo URL" name="icon" defaultValue={currentShop?.icon ?? ''} />
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
          label={!shopId ? 'Create' : 'Update'}
          color={!shopId ? 'primary' : 'secondary'}
          onClick={clickHandler}
        />
      </Box>
    </form>
  );
}
