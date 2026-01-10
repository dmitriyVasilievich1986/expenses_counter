import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import { useParams } from 'react-router';

import { SubmitButton } from '@components/submitButton';
import { useAddressAPIClient } from '@services/apiClient';
import type { AddressPostRequest } from '@services/apiClient/address/types';
import type { AddressType } from '@store/shop';

import { AddressCard } from './AddressCard';

export function AddressesList(props: { addresses: AddressType[] }) {
  const { shopId } = useParams();
  const { postAddress } = useAddressAPIClient();

  const createHandler = () => {
    const data: AddressPostRequest = {
      address: 'address',
      localName: 'localName',
      shopId: parseInt(shopId as string),
    };
    postAddress(data);
  };

  return (
    <>
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
    </>
  );
}
