/**
 * Address list for the shop create/edit screen: renders each address as a card and exposes
 * an action to add another address for the shop resolved from the route `shopId`.
 *
 * @module pages/shop/createShop/addressList/AddressesList
 */

import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { useParams } from 'react-router';

import { SubmitButton } from '@components/submitButton';
import { useAddressAPIClient } from '@services/apiClient';
import type { AddressPostRequest } from '@services/apiClient/address/types';
import type { AddressType } from '@store/shop';

import { AddressCard } from './AddressCard';

/**
 * Renders the shop's addresses inside a paper panel, or nothing when the route has no `shopId`.
 *
 * @param props - Component props.
 * @param props.addresses - Addresses belonging to the current shop (from store).
 * @returns The addresses panel, or `null` if `shopId` is missing from the URL.
 */
export function AddressesList(props: { addresses: AddressType[] }) {
  const { shopId } = useParams();
  const { postCurrentShopAddress } = useAddressAPIClient();

  /** Posts a new address for the shop in the URL via the address API client. */
  const createHandler = () => {
    const data: AddressPostRequest = {
      address: 'address',
      localName: 'localName',
      shopId: parseInt(shopId as string),
    };
    postCurrentShopAddress(data);
  };

  if (!shopId) return null;
  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Typography textAlign="center" variant="h4">
        {'Addresses'}
      </Typography>
      <Stack direction="column" spacing={2} sx={{ mt: 2 }}>
        {props.addresses.map((address) => (
          <AddressCard key={address.id} address={address} />
        ))}
      </Stack>
      <form onSubmit={(e) => e.preventDefault()}>
        <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
          <SubmitButton variant="create" onClick={createHandler} />
        </Box>
      </form>
    </Paper>
  );
}
