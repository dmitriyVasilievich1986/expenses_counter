import * as React from "react";
import axios from "axios";

import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { APIResponseType, API_URLS } from "../../Constants";
import { ProductsForm } from "./ProductsForm";
import { ProductsList } from "./ProductsList";
import { ProductType } from "./types";

export function ProductsPage() {
  const [products, setProducts] = React.useState<ProductType<number>[]>([]);

  React.useEffect(() => {
    axios
      .get(API_URLS.Product)
      .then((data: APIResponseType<ProductType<number>[]>) => {
        setProducts(data.data);
      });
  }, []);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <ProductsList products={products} />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <ProductsForm products={products} setProducts={setProducts} />
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}></Grid>
      </Grid>
    </Box>
  );
}
