/**
 * Single-address editor card: shows fields for one shop address and triggers update/delete via the address API,
 * using `shopId` from the route params.
 *
 * @module pages/shop/createShop/addressList/AddressCard
 */

import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { useRef } from 'react';
import { useParams } from 'react-router';

import { Input } from '@components/input';
import { SubmitButton } from '@components/submitButton';
import { useAddressAPIClient } from '@services/apiClient';
import type { AddressPutRequest } from '@services/apiClient/address/types';
import type { AddressType } from '@store/shop';

/**
 * Renders a paper card with a form to edit an address and buttons to persist or remove it.
 *
 * @param props - Component props.
 * @param props.address - Address row to display and submit updates for.
 * @returns The address edit card UI.
 */
export function AddressCard(props: { address: AddressType }) {
  const { shopId } = useParams();
  const { putCurrentShopAddress, deleteCurrentShopAddress } = useAddressAPIClient();
  const formRef = useRef<HTMLFormElement>(null);

  /** Submits the form as a PUT update for this card's address. */
  const updateHandler = () => {
    const formData = new FormData(formRef.current as HTMLFormElement);
    const data = Object.fromEntries(formData.entries()) as unknown as AddressPutRequest;
    const addressId = props.address.id;
    putCurrentShopAddress(addressId, data);
  };

  /** Deletes this card's address via the API. */
  const deleteHandler = () => {
    const addressId = props.address.id;
    deleteCurrentShopAddress(addressId);
  };

  return (
    <Paper sx={{ p: 2 }}>
      <form style={{ marginTop: '1rem' }} ref={formRef} onSubmit={(e) => e.preventDefault()}>
        <Typography textAlign="center" variant="h4">
          {props.address.localName}
        </Typography>
        <Stack direction="column" spacing={2}>
          <Input label="Address" name="address" defaultValue={props.address.address} />
          <Input label="Local Name" name="localName" defaultValue={props.address.localName} />
          <input type="hidden" name="shopId" value={shopId} />
        </Stack>
        <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
          <Stack direction="row" spacing={1}>
            <SubmitButton label="Delete" color="error" onClick={deleteHandler} />
            <SubmitButton label="Update" color="secondary" onClick={updateHandler} />
          </Stack>
        </Box>
      </form>
    </Paper>
  );
}
