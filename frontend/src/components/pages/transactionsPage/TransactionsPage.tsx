import * as React from "react";
import axios from "axios";

import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { APIResponseType, API_URLS } from "../../Constants";
import { Calendar } from "../../components/calendar";
import { TransactionForm } from "./TransactionForm";
import { TransactionList } from "./TransactionList";
import { ShopAddressType } from "../shopsPage/types";
import { ProductType } from "../productsPage/types";
import { TransactionType } from "./types";

export function TransactionsPage() {
  const [transactions, setTransactions] = React.useState<
    TransactionType<ProductType<number>, ShopAddressType<number>>[]
  >([]);
  const [addresses, setAddresses] = React.useState<ShopAddressType<number>[]>(
    [],
  );
  const [products, setProducts] = React.useState<ProductType<number>[]>([]);

  React.useEffect(() => {
    axios
      .get(API_URLS.Transaction)
      .then(
        (
          data: APIResponseType<
            TransactionType<ProductType<number>, ShopAddressType<number>>[]
          >,
        ) => {
          setTransactions(data.data);
        },
      )
      .catch(() => {
        setTransactions([]);
      });
    axios
      .get(API_URLS.Address)
      .then((data: APIResponseType<ShopAddressType<number>[]>) => {
        setAddresses(data.data);
      })
      .catch(() => {
        setAddresses([]);
      });
    axios
      .get(API_URLS.Product)
      .then((data: APIResponseType<ProductType<number>[]>) => {
        setProducts(data.data);
      })
      .catch(() => {
        setProducts([]);
      });
  }, []);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <TransactionList transactions={transactions} />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <TransactionForm
            addresses={addresses}
            products={products}
            transactions={transactions}
            setTransactions={setTransactions}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}>
          <Calendar />
        </Grid>
      </Grid>
    </Box>
  );
}
