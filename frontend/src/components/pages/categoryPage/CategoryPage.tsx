import React from "react";

import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { CategoriesListContainer } from "./CategoriesList";
import { CategoryForm } from "./CategoryForm";

export function CategoryPage() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <CategoriesListContainer />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <CategoryForm />
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}></Grid>
      </Grid>
    </Box>
  );
}
