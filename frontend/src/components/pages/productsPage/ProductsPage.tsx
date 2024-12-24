import * as React from "react";

import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { ProductsForm } from "./ProductsForm";
import { ProductsList } from "./ProductsList";

export function ProductsPage() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <ProductsList />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <ProductsForm />
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}></Grid>
      </Grid>
    </Box>
  );
}
