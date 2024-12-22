import { useNavigate } from "react-router";
import { useSelector } from "react-redux";
import React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import List from "@mui/material/List";

import { MainReducerType } from "../../reducers/types";

export function ProductsList() {
  const products = useSelector((state: MainReducerType) => state.main.products);
  const navigate = useNavigate();

  return (
    <List>
      {products.map((p) => (
        <ListItemButton
          key={p.id}
          onClick={(_) => navigate(`/create/product/${p!.id}`)}
        >
          <ListItemText primary={p.name} />
        </ListItemButton>
      ))}
    </List>
  );
}
