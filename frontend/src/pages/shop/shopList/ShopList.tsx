import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import axios from 'axios';
import _ from 'lodash';
import { useEffect } from 'react';
import { useNavigate } from 'react-router';

import { useCategoryStore, type CategorySimpleType } from '@store/category';
import { useShopStore, type ShopSimpleType } from '@store/shop';

import { CardsStack } from './cardsStack';

export function ShopList() {
  const shops = useShopStore((state) => state.shops);
  const categories = useCategoryStore((state) => state.categories);

  const navigate = useNavigate();

  useEffect(() => {
    if (shops.length !== 0) return;
    axios
      .get<{
        data: ShopSimpleType[];
      }>(`${import.meta.env.VITE_API_HOST}/api/v1/shop`)
      .then((response) => {
        useShopStore.setState({ shops: response.data.data });
      });
  }, [shops]);

  useEffect(() => {
    if (categories.length !== 0) return;
    axios
      .get<{
        data: CategorySimpleType[];
      }>(`${import.meta.env.VITE_API_HOST}/api/v1/category`)
      .then((response) => {
        useCategoryStore.setState({ categories: response.data.data });
      });
  }, [categories]);

  const shopsByCategory = _.groupBy(shops, (shop) => shop.categoryId);

  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      {Object.keys(shopsByCategory).map((k) => (
        <CardsStack key={k} categoryId={parseInt(k) ?? null} shops={shopsByCategory[k]} />
      ))}
      <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
        <Button variant="contained" color="primary" onClick={() => navigate('/shop/create')}>
          <Typography variant="button">Create</Typography>
        </Button>
      </Box>
    </Container>
  );
}
