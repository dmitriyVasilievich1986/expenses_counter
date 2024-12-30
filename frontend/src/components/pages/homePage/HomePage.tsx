import React from "react";

import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { TransactionsList } from "./TransactionsList";
import { Calendar } from "../../components/calendar";
import { MonthSpendings } from "./MonthSpendings";

export function HomePage() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <MonthSpendings />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <TransactionsList />
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}>
          <Container>
            <Calendar />
          </Container>
        </Grid>
      </Grid>
    </Box>
  );
}
