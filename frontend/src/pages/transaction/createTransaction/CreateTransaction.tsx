/**
 * Transaction create/update form: address and product async pickers, price and count inputs, and submit/delete actions.
 * Uses `currentTransaction` and `currentDate` from the transaction store when editing; parent route supplies `transactionId`.
 *
 * @module pages/transaction/createTransaction/CreateTransaction
 */

import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import dayjs from 'dayjs';
import { useMemo, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router';

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

/**
 * Renders the transaction form with async-loaded addresses and products; creates via POST or updates via PUT.
 *
 * @returns The transaction form wrapped in MUI `Container` / `Paper`.
 */
export function CreateTransaction() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { transactionId } = useParams();
  const formRef = useRef<HTMLFormElement>(null);

  const { currentTransaction } = useTransactionStore();
  const { products, setProducts } = useProductStore();
  const { addresses, setAddresses } = useShopStore();

  const { postTransaction, putTransaction, deleteTransaction } = useTransactionAPIClient();
  const { getAddresses } = useAddressAPIClient();
  const { getProducts } = useProductAPIClient();

  const [address, setAddress] = useState<AddressType | null>(currentTransaction?.address ?? null);

  const [product, setProduct] = useState<ProductSimpleType | null>(
    currentTransaction?.product ?? null
  );

  const currentDate = useMemo(() => {
    const dateParam = searchParams.get('date');
    return dateParam ? dayjs(dateParam) : dayjs();
  }, [searchParams]);

  /** Builds payload from the form and store date, then POST (navigate to new id) or PUT when `transactionId` is set. */
  const clickHandler = async () => {
    const formData = new FormData(formRef.current as HTMLFormElement);
    const data = Object.fromEntries(formData.entries()) as unknown as TransactionPostRequest;
    data.date = currentDate.format('YYYY-MM-DD');
    data.addressId = address!.id;
    data.productId = product!.id;

    if (transactionId === undefined) {
      try {
        const response = await postTransaction(data);
        navigate({ pathname: `/transaction/${response.id}`, search: searchParams.toString() });
      } catch (error) {
        console.error(error);
      }
    } else {
      await putTransaction(parseInt(transactionId), data);
    }
  };

  /** Deletes the transaction for the route id and navigates back to the transaction list. */
  const deleteHandler = async () => {
    await deleteTransaction(parseInt(transactionId as string));
    navigate({ pathname: '/transaction', search: searchParams.toString() });
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
              setItems={setAddresses}
              label="Address"
              nameColumn="localName"
            />
            <AsyncInput<ProductSimpleType>
              value={product}
              onChange={setProduct}
              items={products}
              getItems={getProducts}
              setItems={setProducts}
              label="Product"
              link="/product"
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
              {transactionId && (
                <SubmitButton label="Delete" color="error" onClick={deleteHandler} />
              )}
              <SubmitButton
                label={transactionId ? 'Update' : 'Create'}
                color={transactionId ? 'secondary' : 'primary'}
                onClick={clickHandler}
              />
            </Stack>
          </Box>
        </form>
      </Paper>
    </Container>
  );
}
