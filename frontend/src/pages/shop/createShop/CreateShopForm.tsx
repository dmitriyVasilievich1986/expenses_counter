import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import { useNavigate, useParams } from 'react-router';

import { Input } from '@components/input';
import { useCategoryStore } from '@store/category';
import { useMainStore } from '@store/main';
import { useShopStore } from '@store/shop';
import { SubmitButton } from '@components/submitButton';
import { useRef } from 'react';
import { useShopAPIClient, useCategoryAPIClient } from '@services/apiClient';
import type { ShopPostRequest } from '@services/apiClient/shop/types';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import type { CategorySimpleType } from '@store/category';
import { useState } from 'react';
import CircularProgress from '@mui/material/CircularProgress';

export function CreateShopForm() {
  const currentShop = useShopStore((state) => state.currentShop);
  if (currentShop === null) return null;

  const navigate = useNavigate();
  const { shopId } = useParams();
  const formRef = useRef<HTMLFormElement>(null);

  const [category, setCategory] = useState<CategorySimpleType>(currentShop.category);

  const { postShop, putShop } = useShopAPIClient();
  const { getCategories } = useCategoryAPIClient();

  const categories = useCategoryStore((state) => state.categories);

  const isLoading = useMainStore((state) => state.isLoading);

  const clickHandler = async () => {
    const formData = new FormData(formRef.current as HTMLFormElement);
    const data = Object.fromEntries(formData.entries()) as unknown as ShopPostRequest;
    data.categoryId = category.id;

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

  const handleOpen = async () => {
    await getCategories();
  };

  return (
    <form style={{ marginTop: '1rem' }} ref={formRef} onSubmit={(e) => e.preventDefault()}>
      <Stack direction="column" spacing={2}>
        <Input label="Shop name" name="name" defaultValue={currentShop.name} />
        <Input
          label="Shop description"
          name="description"
          defaultValue={currentShop.description ?? ''}
        />
        <Input label="Shop logo URL" name="icon" defaultValue={currentShop.icon ?? ''} />
        <Autocomplete
          options={categories ?? [category]}
          getOptionLabel={(option) => option.name}
          value={category}
          onOpen={handleOpen}
          onChange={(_, value) => setCategory(value)}
          fullWidth
          disableClearable
          renderInput={(params) => (
            <TextField
              name="categoryId"
              {...params}
              label="Category"
              slotProps={{
                input: {
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {isLoading ? <CircularProgress color="inherit" size={20} /> : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                },
              }}
            />
          )}
        />
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
