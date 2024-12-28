import { useSearchParams } from "react-router-dom";
import * as React from "react";
import axios from "axios";

import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { APIResponseType, API_URLS } from "../../Constants";
import { Calendar } from "../../components/calendar";
import { ShopAddressType } from "../shopsPage/types";
import { CategoryType } from "../categoryPage/types";
import { TransactionForm } from "./TransactionForm";
import { TransactionList } from "./TransactionList";
import { ProductType } from "../productsPage/types";
import { TransactionType } from "./types";

export function TransactionsPage() {
  const [transactions, setTransactions] = React.useState<
    TransactionType<ProductType<number>, ShopAddressType<number>>[]
  >([]);
  const [addresses, setAddresses] = React.useState<ShopAddressType<number>[]>(
    [],
  );
  const [products, setProducts] = React.useState<
    ProductType<CategoryType<number>>[]
  >([]);
  const [popularProducts, setPopularProducts] = React.useState<
    TransactionType<ProductType<number>, ShopAddressType<number>>[]
  >([]);

  const [searchParams, _] = useSearchParams();

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
      .then((data: APIResponseType<ProductType<CategoryType<number>>[]>) => {
        setProducts(data.data);
      })
      .catch(() => {
        setProducts([]);
      });
  }, []);

  React.useEffect(() => {
    const address = searchParams.get("address");
    if (!!address) {
      axios
        .post(`${API_URLS.ProductPopular}`, { address })
        .then(
          (
            data: APIResponseType<
              TransactionType<ProductType<number>, ShopAddressType<number>>[]
            >,
          ) => {
            setPopularProducts(data.data);
          },
        )
        .catch(() => setPopularProducts([]));
    } else {
      setPopularProducts([]);
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
