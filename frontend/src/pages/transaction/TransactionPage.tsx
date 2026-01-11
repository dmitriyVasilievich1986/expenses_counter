import Grid from '@mui/material/Grid';
import { useEffect } from 'react';
import { useParams } from 'react-router';

import { useTransactionAPIClient } from '@services/apiClient/transaction';
import { useTransactionStore } from '@store/transaction';

import { CreateTransaction } from './CreateTransaction';
import { LeftSide } from './LeftSide';
import { RightSide } from './rightSide';

export function TransactionPage() {
  const { transactionId } = useParams();
  const { getTransaction } = useTransactionAPIClient();
  const { setCurrentTransaction, currentTransaction } = useTransactionStore();

  useEffect(() => {
    if (transactionId) {
      getTransaction(parseInt(transactionId));
    } else {
      setCurrentTransaction(null);
    }

    return () => {
      setCurrentTransaction(null);
    };
  }, [transactionId]);

  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 4, lg: 3 }}>
        <LeftSide />
      </Grid>
      <Grid size={{ xs: 12, md: 8, lg: 6 }}>
        {transactionId && !currentTransaction ? null : <CreateTransaction />}
      </Grid>
      <Grid size={{ xs: 12, md: 12, lg: 3 }}>
        <RightSide />
      </Grid>
    </Grid>
  );
}
