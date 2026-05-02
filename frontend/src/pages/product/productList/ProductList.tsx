/**
 * Product list page: load products and categories, group products by category, and render stacks with navigation to detail and create.
 */

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import _ from 'lodash';
import { useEffect } from 'react';
import { useNavigate } from 'react-router';

import { CardsStack } from '@components/cardsStack';
import { useProductAPIClient, useCategoryAPIClient } from '@services/apiClient';
import { useCategoryStore } from '@store/category';
import { useProductStore } from '@store/product';

/**
 * Render products grouped by category as card stacks and a create button.
 *
 * @returns {JSX.Element} The product list layout inside a container.
 */
export function ProductList() {
  const products = useProductStore((state) => state.products);
  const categories = useCategoryStore((state) => state.categories);

  const { getProducts } = useProductAPIClient();
  const { getCategories } = useCategoryAPIClient();

  const navigate = useNavigate();

  useEffect(() => {
    if (products === null) getProducts();
  }, [products]);

  useEffect(() => {
    if (categories === null) getCategories();
  }, [categories]);

  const productsByCategory = _.groupBy(products ?? [], (product) => product.categoryId);

  return (
    <Container maxWidth="lg" sx={{ mt: 2 }}>
      {Object.keys(productsByCategory).map((k) => (
        <CardsStack
          key={k}
          categoryId={parseInt(k) ?? null}
          items={productsByCategory[k]}
          onClick={(item) => navigate(`/product/${item.id}`)}
        />
      ))}
      <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
        <Button variant="contained" color="primary" onClick={() => navigate('/product/create')}>
          <Typography variant="button">Create</Typography>
        </Button>
      </Box>
    </Container>
  );
}
