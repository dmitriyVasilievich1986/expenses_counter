/**
 * Transaction section layout: calendar / navigation on the left, create-or-edit transaction in the center,
 * supplementary panel on the right.
 *
 * @module pages/transaction/TransactionPage
 */

import Grid from '@mui/material/Grid';

import { CreateTransactionPage } from './createTransaction';
import { LeftSide } from './LeftSide';
import { RightSide } from './rightSide';

/**
 * Renders a three-column MUI `Grid` with {@link LeftSide}, {@link CreateTransactionPage}, and {@link RightSide}.
 *
 * @returns The transaction workspace shell.
 */
export function TransactionPage() {
  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12, md: 4, lg: 3 }}>
        <LeftSide />
      </Grid>
      <Grid size={{ xs: 12, md: 8, lg: 6 }}>
        <CreateTransactionPage />
      </Grid>
      <Grid size={{ xs: 12, md: 12, lg: 3 }}>
        <RightSide />
      </Grid>
    </Grid>
  );
}
