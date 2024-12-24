import * as React from "react";

import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { Calendar } from "../../components/calendar";
import { TransactionForm } from "./TransactionForm";
import { TransactionList } from "./TransactionList";

export function TransactionsPage() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <TransactionList />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <TransactionForm />
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}>
          <Calendar />
        </Grid>
      </Grid>
    </Box>
  );
}
