import { useSearchParams } from "react-router-dom";
import * as React from "react";
import axios from "axios";

import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { APIResponseType, API_URLS } from "../../Constants";
import { ProductTypeDetailed } from "../productsPage/types";
import { ShopAddressTypeNumber } from "../shopsPage/types";
import { Calendar } from "../../components/calendar";
import { TransactionForm } from "./TransactionForm";
import { TransactionList } from "./TransactionList";
import { TransactionTypeNumber } from "./types";

export function TransactionsPage() {
  const [transactions, setTransactions] = React.useState<
    TransactionTypeNumber[]
  >([]);
  const [addresses, setAddresses] = React.useState<ShopAddressTypeNumber[]>([]);
  const [products, setProducts] = React.useState<ProductTypeDetailed[]>([]);
  const [popularProducts, setPopularProducts] = React.useState<
    TransactionTypeNumber[]
  >([]);

  const [searchParams, _] = useSearchParams();

  React.useEffect(() => {
    axios
      .get(API_URLS.Address)
      .then((data: APIResponseType<ShopAddressTypeNumber[]>) => {
        setAddresses(data.data);
      })
      .catch(() => {
        setAddresses([]);
      });
    axios
      .get(API_URLS.Product)
      .then((data: APIResponseType<ProductTypeDetailed[]>) => {
        setProducts(data.data);
      })
      .catch(() => {
        setProducts([]);
      });
  }, []);

  React.useEffect(() => {
    const currentDate: string | undefined = searchParams.get("currentDate");
    const address = searchParams.get("address");

    if (!!address) {
      axios
        .post(`${API_URLS.ProductPopular}`, { address })
        .then((data: APIResponseType<TransactionTypeNumber[]>) => {
          setPopularProducts(data.data);
        })
        .catch(() => setPopularProducts([]));
    } else {
      setPopularProducts([]);
    }
    if (!!currentDate) {
      axios
        .post(`${API_URLS.ProductPopular}`, { address })
        .then((data: APIResponseType<TransactionTypeNumber[]>) => {
          setTransactions(data.data);
        })
        .catch(() => setTransactions([]));
    } else {
      setTransactions([]);
    }
  }, [searchParams]);

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
          <Typography variant="h6" align="center">
            Popular Products:
          </Typography>
          <TransactionList transactions={popularProducts} />
        </Grid>
      </Grid>
    </Box>
  );
}
