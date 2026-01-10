import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import { useEffect } from 'react';
import { useParams } from 'react-router';

import { useShopStore } from '@store/shop';
import { AddressesList } from './addressList';
import { useShopAPIClient } from '@services/apiClient';

import { CreateShopForm } from './CreateShopForm';

export function CreateShop() {
  const { shopId } = useParams();
  const { currentShop, setCurrentShop } = useShopStore();
  const { getShop } = useShopAPIClient();

  useEffect(() => {
    if (shopId && currentShop === null) getShop(parseInt(shopId));

    // Cleanup function: clear currentShop when component unmounts
    return () => {
      setCurrentShop(null);
    };
  }, [shopId]);

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
      <AddressesList addresses={currentShop?.addresses ?? []} />
    </Container>
  );
}
