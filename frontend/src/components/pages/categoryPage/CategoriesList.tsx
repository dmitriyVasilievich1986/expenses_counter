import { useNavigate, useParams } from "react-router";
import React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { CategoryType } from "./types";

function CategoriesList(props: {
  categories: CategoryType<number>[];
  parent: number | null;
}) {
  const { categoryId } = useParams();
  let navigate = useNavigate();

  const filteredCategories = props.categories.filter(
    (c) => c.parent === props.parent,
  );

  if (filteredCategories.length == 0) {
    return null;
  }
  return (
    <List sx={{ pl: 2 }}>
      {filteredCategories.map((c) => (
        <Box key={c.id}>
          <ListItemButton
            onClick={(_) => navigate(`/create/category/${c.id}`)}
            sx={
              categoryId !== undefined && c.id === parseInt(categoryId)
                ? { backgroundColor: "#bbdefb" }
                : {}
            }
          >
            <ListItemText primary={c.name} />
          </ListItemButton>
          <CategoriesList
            parent={c.id as number}
            categories={props.categories}
          />
        </Box>
      ))}
    </List>
  );
}

export function CategoriesListContainer(props: {
  categories: CategoryType<number>[];
}) {
  return <CategoriesList {...props} parent={null} />;
}
