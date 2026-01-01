import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import axios from 'axios';
import { useEffect } from 'react';
import { useParams } from 'react-router';

import { useCategoryStore, type CategorySimpleType } from '@store/category';
import { useMainStore } from '@store/main';
import { useShopStore, type ShopType } from '@store/shop';

import { CreateShopForm } from './CreateShopForm';

export function CreateShop() {
  const { shopId } = useParams();
  const currentShop = useShopStore((state) => state.currentShop);
  const setCurrentShop = useShopStore((state) => state.setCurrentShop);
  const setIsLoading = useMainStore((state) => state.setIsLoading);
  const categories = useCategoryStore((state) => state.categories);
  const addCategories = useCategoryStore((state) => state.addCategories);

  useEffect(() => {
    if (shopId) {
      setIsLoading(true);
      axios
        .get<ShopType>(`${import.meta.env.VITE_API_HOST}/api/v1/shop/${shopId}`)
        .then((response) => {
          setCurrentShop(response.data);
        })
        .finally(() => setIsLoading(false));
    }

    // Cleanup function: clear currentShop when component unmounts
    return () => {
      useShopStore.setState({ currentShop: null });
    };
  }, [shopId]);

  useEffect(() => {
    if (categories.length !== 0) return;
    axios
      .get<{ data: CategorySimpleType[] }>(`${import.meta.env.VITE_API_HOST}/api/v1/category`)
      .then((response) => {
        addCategories(response.data.data);
      });
  }, [categories]);

  if (shopId && !currentShop) {
    return (
      <Typography textAlign="center" variant="h4">
        Shop not found
      </Typography>
    );
  }
  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 2, mt: 2 }}>
        <Typography textAlign="center" variant="h4">
          {currentShop ? currentShop.name : 'Create Shop'}
        </Typography>
        <CreateShopForm />
      </Paper>
    </Container>
  );
}
