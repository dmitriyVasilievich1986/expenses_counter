import * as React from "react";
import axios from "axios";

import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import { APIResponseType, API_URLS } from "../../Constants";
import { CategoriesListContainer } from "./CategoriesList";
import { CategoryForm } from "./CategoryForm";
import { CategoryType } from "./types";

export function CategoryPage() {
  const [categories, setCategories] = React.useState<CategoryType[]>([]);

  React.useEffect(() => {
    axios
      .get(API_URLS.Category)
      .then((data: APIResponseType<CategoryType[]>) =>
        setCategories(data.data),
      );
  }, []);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <CategoriesListContainer categories={categories} />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <CategoryForm categories={categories} setCategories={setCategories} />
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}></Grid>
      </Grid>
    </Box>
  );
}
