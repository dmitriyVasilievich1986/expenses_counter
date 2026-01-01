import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Stack from '@mui/material/Stack';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router';

import { Input } from '@components/input';
import { useCategoryStore } from '@store/category';
import { useMainStore } from '@store/main';
import { useShopStore, type ShopType } from '@store/shop';


export function CreateShopForm() {
  const navigate = useNavigate();
  const { shopId } = useParams();

  const setCurrentShop = useShopStore((state) => state.setCurrentShop);
  const updateShop = useShopStore((state) => state.updateShop);
  const addShops = useShopStore((state) => state.addShops);
  const currentShop = useShopStore((state) => state.currentShop);

  const categories = useCategoryStore((state) => state.categories);

  const isLoading = useMainStore((state) => state.isLoading);
  const setIsLoading = useMainStore((state) => state.setIsLoading);

  const submitHandler = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.target as HTMLFormElement);
    const data = Object.fromEntries(formData.entries());
    setIsLoading(true);
    const method = shopId ? 'put' : 'post';
    const url = shopId
      ? `${import.meta.env.VITE_API_HOST}/api/v1/shop/${shopId}`
      : `${import.meta.env.VITE_API_HOST}/api/v1/shop`;
    axios
      .request<ShopType>({
        method,
        url,
        data,
      })
      .then((response) => {
        setCurrentShop(response.data);
        if (method === 'put') {
          updateShop(response.data);
        } else {
          addShops([response.data]);
        }
        navigate(`/shop/${response.data.id}`);
      })
      .catch((error) => {
        console.error('error', error);
      })
      .finally(() => setIsLoading(false));
  };

  return (
    <form style={{ marginTop: '1rem' }} onSubmit={submitHandler}>
      <Stack direction="column" spacing={2}>
        <Input label="Shop name" name="name" defaultValue={currentShop?.name} />
        <Input
          label="Shop description"
          name="description"
          defaultValue={currentShop?.description}
        />
        <Input label="Shop logo URL" name="icon" defaultValue={currentShop?.icon} />
        {categories.length !== 0 && (
          <Select
            name="categoryId"
            defaultValue={currentShop?.categoryId ?? categories[0].id}
            fullWidth
          >
            {categories.map((category) => (
              <MenuItem key={category.id} value={category.id}>
                {category.name}
              </MenuItem>
            ))}
          </Select>
        )}
      </Stack>
      <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
        <Button type="submit" variant="contained" color="primary" disabled={isLoading}>
          {isLoading ? <CircularProgress size={20} /> : 'Submit'}
        </Button>
      </Box>
    </form>
  );
}
