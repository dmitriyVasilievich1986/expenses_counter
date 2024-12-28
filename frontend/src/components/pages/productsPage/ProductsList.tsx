import { useNavigate } from "react-router-dom";
import React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import List from "@mui/material/List";

import { ProductTypeDetailed } from "./types";
import { PagesURLs } from "../../Constants";

export function ProductsList(props: { products: ProductTypeDetailed[] }) {
  const navigate = useNavigate();

  return (
    <List>
      {props.products.map((p) => (
        <ListItemButton
          key={p.id}
          onClick={(_) => navigate(`${PagesURLs.Product}/${p!.id}`)}
        >
          <ListItemText primary={p.name} />
        </ListItemButton>
      ))}
    </List>
  );
}
