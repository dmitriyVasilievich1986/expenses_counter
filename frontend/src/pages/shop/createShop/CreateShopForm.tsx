import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import { useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router';

import { CategoryInput } from '@components/categoryInput';
import { Input } from '@components/input';
import { SubmitButton } from '@components/submitButton';
import { useShopAPIClient } from '@services/apiClient';
import type { ShopPostRequest } from '@services/apiClient/shop/types';
import type { CategorySimpleType } from '@store/category';
import { useMainStore } from '@store/main';
import { useShopStore } from '@store/shop';

export function CreateShopForm() {
  const navigate = useNavigate();
  const { shopId } = useParams();
  const formRef = useRef<HTMLFormElement>(null);

  const currentShop = useShopStore((state) => state.currentShop);
  const [category, setCategory] = useState<CategorySimpleType | null>(
    currentShop?.category ?? null
  );

  const { postShop, putShop } = useShopAPIClient();

  const isLoading = useMainStore((state) => state.isLoading);

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
        <CategoryInput value={category} onChange={setCategory} />
      </Stack>
      <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
        <SubmitButton
          disabled={isLoading}
          variant={!shopId ? 'create' : 'update'}
          onClick={clickHandler}
        />
      </Box>
    </form>
  );
}
