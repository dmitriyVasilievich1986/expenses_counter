import { useNavigate } from "react-router";
import { useSelector } from "react-redux";
import React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import List from "@mui/material/List";

import {
  MainReducerType,
  TransactionType,
  ProductType,
} from "../../reducers/types";

function Transaction(props: { transaction: TransactionType }) {
  const products = useSelector((state: MainReducerType) => state.main.products);
  let navigate = useNavigate();
  const product = products.find(
    (p) => p.id === props.transaction.product,
  ) as ProductType;

  return (
    <ListItemButton
      onClick={() => navigate(`/create/transaction/${props.transaction.id}`)}
    >
      <ListItemText
        primary={`${product.name}: ${
          props.transaction.price * props.transaction.count
        }`}
      />
    </ListItemButton>
  );
}

export function TransactionList() {
  const transactions = useSelector(
    (state: MainReducerType) => state.main.transactions,
  );

  if (transactions.length === 0) return null;
  return (
    <List sx={{ pl: 2 }}>
      {transactions.map((t) => (
        <Transaction transaction={t} key={t.id} />
      ))}
    </List>
  );
}
