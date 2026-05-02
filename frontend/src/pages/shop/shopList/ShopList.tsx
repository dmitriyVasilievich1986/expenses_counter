/**
 * Shop list page: load shops and categories, group shops by category, and render stacks with navigation to detail and create.
 */

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import _ from 'lodash';
import { useEffect } from 'react';
import { useNavigate } from 'react-router';

import { CardsStack } from '@components/cardsStack';
import { useShopAPIClient, useCategoryAPIClient } from '@services/apiClient';
import { useCategoryStore } from '@store/category';
import { useShopStore } from '@store/shop';

/**
 * Render shops grouped by category as card stacks and a create button.
 *
 * @returns {JSX.Element} The shop list layout inside a container.
 */
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
        <CardsStack
          key={k}
          categoryId={parseInt(k) ?? null}
          items={shopsByCategory[k]}
          onClick={(item) => navigate(`/shop/${item.id}`)}
        />
      ))}
      <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
        <Button variant="contained" color="primary" onClick={() => navigate('/shop/create')}>
          <Typography variant="button">Create</Typography>
        </Button>
      </Box>
    </Container>
  );
}
