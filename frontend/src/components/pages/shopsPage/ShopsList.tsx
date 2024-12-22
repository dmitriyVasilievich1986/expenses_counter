import { useNavigate } from "react-router";
import { useSelector } from "react-redux";
import React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import {
  MainReducerType,
  ShopAddressType,
  ShopType,
} from "../../reducers/types";

function Addresses(props: { addresses: ShopAddressType[] }) {
  let navigate = useNavigate();

  if (props.addresses.length === 0) return null;
  return (
    <List sx={{ ml: 4 }}>
      {props.addresses.map((a) => (
        <ListItemButton
          onClick={() => navigate(`/create/shop/${a.shop}/address/${a.id}`)}
          key={a.id}
        >
          <ListItemText primary={a.address} />
        </ListItemButton>
      ))}
    </List>
  );
}

function Shop(props: { shop: ShopType }) {
  let navigate = useNavigate();
  const addresses = useSelector(
    (state: MainReducerType) => state.main.addresses,
  );
  const filteredAddresses = addresses.filter((a) => a.shop === props.shop.id);

  return (
    <Box>
      <ListItemButton onClick={() => navigate(`/create/shop/${props.shop.id}`)}>
        <ListItemText primary={props.shop.name} />
      </ListItemButton>
      <Addresses addresses={filteredAddresses} />
    </Box>
  );
}

export function ShopsList() {
  const shops = useSelector((state: MainReducerType) => state.main.shops);

  if (shops.length === 0) return null;
  return (
    <List sx={{ pl: 2 }}>
      {shops.map((shop) => (
        <Shop shop={shop} key={shop.id} />
      ))}
    </List>
  );
}
