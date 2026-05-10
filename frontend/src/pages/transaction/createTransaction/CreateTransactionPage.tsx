/**
 * Transaction create/edit route shell: when `transactionId` is in the URL, fetches that transaction into the store;
 * otherwise clears the current transaction. Shows a skeleton while loading, then renders {@link CreateTransaction}.
 * Clears the selected transaction from the store on unmount.
 *
 * @module pages/transaction/createTransaction/CreateTransactionPage
 */

import Container from '@mui/material/Container';
import Skeleton from '@mui/material/Skeleton';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router';

import { useTransactionAPIClient } from '@services/apiClient/transaction';
import { useTransactionStore } from '@store/transaction';

import { CreateTransaction } from './CreateTransaction';

/**
 * Resolves the transaction from the route (if any), updates {@link useTransactionStore}, and renders the form shell.
 *
 * @returns A loading skeleton while fetching by id, or {@link CreateTransaction} when ready.
 */
export function CreateTransactionPage() {
  const { transactionId } = useParams();

  const { getTransaction } = useTransactionAPIClient();

  const { setCurrentTransaction } = useTransactionStore();

  const [isLoading, setIsLoading] = useState<boolean>(!!transactionId);

  useEffect(() => {
    if (transactionId) {
      getTransaction(parseInt(transactionId))
        .then((transaction) => {
          setCurrentTransaction(transaction);
        })
        .catch((error) => {
          console.error(error);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setCurrentTransaction(null);
    }

    return () => {
      setCurrentTransaction(null);
    };
  }, [transactionId]);

  if (isLoading) {
    return (
      <Container maxWidth="md" sx={{ mt: 2 }}>
        <Skeleton variant="rectangular" sx={{ width: '100%', height: '400px' }} />
      </Container>
    );
  }

  return <CreateTransaction />;
}
