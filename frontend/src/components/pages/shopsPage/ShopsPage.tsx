import React from "react";

import Stack from "@mui/material/Stack";
import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { AddressForm } from "./AddressForm";
import { ShopsList } from "./ShopsList";
import { ShopForm } from "./ShopForm";

export function ShopsPage() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <ShopsList />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <Stack spacing={2}>
            <ShopForm />
            <AddressForm />
          </Stack>
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}></Grid>
      </Grid>
    </Box>
  );
}
