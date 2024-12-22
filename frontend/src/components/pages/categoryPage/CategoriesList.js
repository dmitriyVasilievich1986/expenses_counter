import { useNavigate, useParams } from "react-router";
import { useSelector } from "react-redux";
import React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

function CategoriesList(props) {
  const categories = useSelector((state) => state.main.categories);
  const { categoryId } = useParams();
  let navigate = useNavigate();

  const filteredCategories = categories.filter((c) => c.parent == props.parent);

  if (filteredCategories.length == 0) {
    return null;
  }
  return (
    <List sx={{ pl: 2 }}>
      {filteredCategories.map((c) => (
        <Box key={c.id}>
          <ListItemButton
            onClick={(_) => navigate(`/create/category/${c.id}`)}
            sx={categoryId == c.id ? { backgroundColor: "#bbdefb" } : {}}
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
