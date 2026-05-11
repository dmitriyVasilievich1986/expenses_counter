/**
 * Shop create/edit page: loads the shop from the route `shopId` when present, shows the shop form and address list,
 * and clears the selected shop from store on unmount.
 *
 * @module pages/shop/createShop/CreateShop
 */

import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Typography from '@mui/material/Typography';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router';

import { useShopAPIClient } from '@services/apiClient';
import { useShopStore } from '@store/shop';

import { AddressesList } from './addressList';
import { CreateShopForm } from './CreateShopForm';

/**
 * Renders loading placeholders, a not-found state, or the shop form with addresses depending on route and store.
 *
 * @returns The shop page shell, or skeleton / error UI while resolving data.
 */
export function CreateShop() {
  const { shopId } = useParams();

  const { currentShop, setCurrentShop } = useShopStore();

  const [isLoading, setIsLoading] = useState<boolean>(!!shopId);

  const { getShop } = useShopAPIClient();

  useEffect(() => {
    if (shopId && currentShop === null) {
      getShop(parseInt(shopId))
        .then((shop) => {
          setCurrentShop(shop);
        })
        .catch((error) => {
          console.error(error);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }

    return () => {
      setCurrentShop(null);
    };
  }, [shopId]);

  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ mt: 2 }}>
        <Skeleton variant="rectangular" sx={{ width: '100%', height: '400px' }} />
        {shopId && (
          <Skeleton variant="rectangular" sx={{ width: '100%', height: '200px', mt: 2 }} />
        )}
      </Container>
    );
  }
  if (shopId && !currentShop) {
    return (
      <Container maxWidth="md">
        <Typography textAlign="center" variant="h4">
          Shop not found
        </Typography>
      </Container>
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
