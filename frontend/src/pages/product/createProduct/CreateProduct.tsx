/**
 * Product create/edit page: loads the product from the route `productId` when present, shows the product form,
 * and clears the selected product from store on unmount.
 *
 * @module pages/product/createProduct/CreateProduct
 */

import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Typography from '@mui/material/Typography';
import { useEffect } from 'react';
import { useParams } from 'react-router';

import { useProductAPIClient } from '@services/apiClient';
import { useProductStore } from '@store/product';

import { CreateProductForm } from './CreateProductForm';

/**
 * Renders loading placeholders, a not-found state, or the product form depending on route and store.
 *
 * @returns The product page shell, or skeleton / error UI while resolving data.
 */
export function CreateProduct() {
  const { productId } = useParams();

  const { currentProduct, setCurrentProduct, productListLoading } = useProductStore();

  const { getProduct } = useProductAPIClient();

  useEffect(() => {
    if (productId && currentProduct === null) getProduct(parseInt(productId));

    // Cleanup function: clear currentProduct when component unmounts
    return () => {
      setCurrentProduct(null);
    };
  }, [productId]);

  if (productListLoading) {
    return (
      <Container maxWidth="md" sx={{ mt: 2 }}>
        <Skeleton variant="rectangular" sx={{ width: '100%', height: '400px' }} />
      </Container>
    );
  }
  if (productId && !currentProduct) {
    return (
      <Container maxWidth="md" sx={{ mt: 2 }}>
        <Typography textAlign="center" variant="h4">
          Product not found
        </Typography>
      </Container>
    );
  }
  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 2, mt: 2 }}>
        <Typography textAlign="center" variant="h4">
          {currentProduct ? currentProduct.name : 'Create Product'}
        </Typography>
        <CreateProductForm />
      </Paper>
    </Container>
  );
}
