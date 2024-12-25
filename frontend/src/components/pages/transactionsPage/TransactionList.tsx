import { useNavigate } from "react-router";
import React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import List from "@mui/material/List";

import { ShopAddressType } from "../shopsPage/types";
import { ProductType } from "../productsPage/types";
import { PagesURLs } from "../../Constants";
import { TransactionType } from "./types";

function Transaction(props: {
  transaction: TransactionType<ProductType<number>, ShopAddressType<number>>;
}) {
  let navigate = useNavigate();

  return (
    <ListItemButton
      onClick={() =>
        navigate(`${PagesURLs.Transaction}/${props.transaction.id}`)
      }
    >
      <ListItemText
        primary={`${props.transaction.product.name}: ${
          props.transaction.price * props.transaction.count
        }`}
      />
    </ListItemButton>
  );
}

export function TransactionList(props: {
  transactions: TransactionType<ProductType<number>, ShopAddressType<number>>[];
}) {
  if (props.transactions.length === 0) return null;
  return (
    <List sx={{ pl: 2 }}>
      {props.transactions.map((t) => (
        <Transaction transaction={t} key={t.id} />
      ))}
    </List>
  );
}
