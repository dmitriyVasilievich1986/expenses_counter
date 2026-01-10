import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import { useEffect } from 'react';
import { useParams } from 'react-router';

import { useProductAPIClient } from '@services/apiClient';
import { useProductStore } from '@store/product';

import { CreateProductForm } from './CreateProductForm';

export function CreateProduct() {
  const { productId } = useParams();
  const { currentProduct, setCurrentProduct } = useProductStore();
  const { getProduct } = useProductAPIClient();

  useEffect(() => {
    if (productId && currentProduct === null) getProduct(parseInt(productId));

    // Cleanup function: clear currentProduct when component unmounts
    return () => {
      setCurrentProduct(null);
    };
  }, [productId]);

  if (productId && !currentProduct) {
    return (
      <Typography textAlign="center" variant="h4">
        Product not found
      </Typography>
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
