import { useSearchParams } from "react-router-dom";
import * as React from "react";
import axios from "axios";

import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { PopularProductsList, TransactionList } from "./TransactionList";
import { APIResponseType, API_URLS } from "../../Constants";
import { Calendar } from "../../components/calendar";
import { TransactionForm } from "./TransactionForm";
import { TransactionTypeNumber } from "./types";

export function TransactionsPage() {
  const [transactions, setTransactions] = React.useState<
    TransactionTypeNumber[]
  >([]);
  const [searchParams] = useSearchParams();

  React.useEffect(() => {
    const currentDate = searchParams.get("currentDate");
    if (!currentDate) {
      setTransactions([]);
      return;
    }
    axios
      .post(API_URLS.TransactionDateRange, {
        start_date: currentDate,
        end_date: currentDate,
      })
      .then((data: APIResponseType<TransactionTypeNumber[]>) => {
        setTransactions(data.data);
      })
      .catch(() => setTransactions([]));
  }, [searchParams]);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <TransactionList
            transactions={transactions}
            setTransactions={setTransactions}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <TransactionForm setTransactions={setTransactions} />
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}>
          <Calendar />
          <PopularProductsList />
        </Grid>
      </Grid>
    </Box>
  );
}
