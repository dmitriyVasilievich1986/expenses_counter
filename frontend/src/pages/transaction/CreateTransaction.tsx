import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import { useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router';

import { AsyncInput } from '@components/asyncInput';
import { Input } from '@components/input';
import { SubmitButton } from '@components/submitButton';
import { useAddressAPIClient } from '@services/apiClient';
import { useProductAPIClient } from '@services/apiClient/product/client';
import { useTransactionAPIClient } from '@services/apiClient/transaction';
import type { TransactionPostRequest } from '@services/apiClient/transaction/types';
import { useProductStore, type ProductSimpleType } from '@store/product';
import { useShopStore, type AddressType } from '@store/shop';
import { useTransactionStore } from '@store/transaction';

export function CreateTransaction() {
  const navigate = useNavigate();
  const { transactionId } = useParams();
  const formRef = useRef<HTMLFormElement>(null);

  const { currentTransaction, currentDate } = useTransactionStore();

  const { postTransaction, putTransaction, deleteTransaction } = useTransactionAPIClient();

  const { getAddresses } = useAddressAPIClient();
  const { addresses } = useShopStore();
  const [address, setAddress] = useState<AddressType | null>(currentTransaction?.address ?? null);

  const { getProducts } = useProductAPIClient();
  const { products } = useProductStore();
  const [product, setProduct] = useState<ProductSimpleType | null>(
    currentTransaction?.product ?? null
  );

  const clickHandler = async () => {
    const formData = new FormData(formRef.current as HTMLFormElement);
    const data = Object.fromEntries(formData.entries()) as unknown as TransactionPostRequest;
    data.date = currentDate.format('YYYY-MM-DD');
    data.addressId = address!.id;
    data.productId = product!.id;

    if (transactionId === undefined) {
      try {
        const response = await postTransaction(data);
        navigate(`/transaction/${response.id}`);
      } catch (error) {
        console.error(error);
      }
    } else {
      await putTransaction(parseInt(transactionId), data);
    }
  };

  const deleteHandler = async () => {
    await deleteTransaction(parseInt(transactionId as string));
    navigate('/transaction');
  };

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 2, mt: 2 }}>
        <form style={{ marginTop: '1rem' }} ref={formRef} onSubmit={(e) => e.preventDefault()}>
          <Stack direction="column" spacing={2}>
            <AsyncInput<AddressType>
              value={address}
              onChange={setAddress}
              items={addresses}
              getItems={getAddresses}
              label="Address"
              nameColumn="localName"
            />
            <AsyncInput<ProductSimpleType>
              value={product}
              onChange={setProduct}
              items={products}
              getItems={getProducts}
              label="Product"
            />
            <Input
              label="Product price"
              name="price"
              defaultValue={currentTransaction?.price.toString() ?? ''}
            />
            <Input
              label="Products count"
              name="count"
              defaultValue={currentTransaction?.count.toString() ?? ''}
            />
          </Stack>
          <Box sx={{ display: 'flex', justifyContent: 'end', mt: 2 }}>
            <Stack direction="row" spacing={1}>
              {transactionId && <SubmitButton variant="delete" onClick={deleteHandler} />}
              <SubmitButton variant={transactionId ? 'update' : 'create'} onClick={clickHandler} />
            </Stack>
          </Box>
        </form>
      </Paper>
    </Container>
  );
}
