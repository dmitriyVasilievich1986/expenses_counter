import { useNavigate, useParams } from "react-router";
import { useSelector } from "react-redux";
import React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { MainReducerType } from "../../reducers/types";

function CategoriesList(props: { parent: number | null }) {
  const categories = useSelector(
    (state: MainReducerType) => state.main.categories,
  );
  const { categoryId } = useParams();
  let navigate = useNavigate();

  const filteredCategories = categories.filter(
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
              c.id === parseInt(categoryId)
                ? { backgroundColor: "#bbdefb" }
                : {}
            }
          >
            <ListItemText primary={c.name} />
          </ListItemButton>
          <CategoriesList parent={c.id} />
        </Box>
      ))}
    </List>
  );
}

export function CategoriesListContainer() {
  return <CategoriesList parent={null} />;
}
