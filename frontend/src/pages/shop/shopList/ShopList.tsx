import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import _ from 'lodash';
import { useEffect } from 'react';
import { useNavigate } from 'react-router';

import { useCategoryStore } from '@store/category';
import { useShopStore } from '@store/shop';

import { CardsStack } from './cardsStack';
import { useShopAPIClient, useCategoryAPIClient } from '@services/apiClient';

export function ShopList() {
  const shops = useShopStore((state) => state.shops);
  const categories = useCategoryStore((state) => state.categories);

  const { getShops } = useShopAPIClient();
  const { getCategories } = useCategoryAPIClient();

  const navigate = useNavigate();

  useEffect(() => {
    if (shops === null) getShops();
  }, [shops]);

  useEffect(() => {
    if (categories === null) getCategories();
  }, [categories]);

  const shopsByCategory = _.groupBy(shops ?? [], (shop) => shop.categoryId);

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
