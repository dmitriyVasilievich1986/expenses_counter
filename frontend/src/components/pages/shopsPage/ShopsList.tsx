import { useNavigate } from "react-router";
import React from "react";

import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { ShopAddressType, ShopType, ShopProps } from "./types";
import { PagesURLs } from "../../Constants";

function Addresses(props: { addresses: ShopAddressType<number>[] }) {
  let navigate = useNavigate();

  if (props.addresses.length === 0) return null;
  return (
    <List sx={{ ml: 4 }}>
      {props.addresses.map((a) => (
        <ListItemButton
          onClick={() =>
            navigate(`${PagesURLs.Shop}/${a.shop}/${PagesURLs.Address}/${a.id}`)
          }
          key={a.id}
        >
          <ListItemText primary={a.address} />
        </ListItemButton>
      ))}
    </List>
  );
}

function Shop(props: ShopProps & { shop: ShopType<number> }) {
  let navigate = useNavigate();
  const filteredAddresses = props.addresses.filter(
    (a) => a.shop === props.shop.id,
  );

  return (
    <Box>
      <ListItemButton
        onClick={() => navigate(`${PagesURLs.Shop}/${props.shop.id}`)}
      >
        <ListItemText primary={props.shop.name} />
      </ListItemButton>
      <Addresses addresses={filteredAddresses} />
    </Box>
  );
}

export function ShopsList(props: ShopProps) {
  if (props.shops.length === 0) return null;
  return (
    <List sx={{ pl: 2 }}>
      {props.shops.map((shop) => (
        <Shop shop={shop} {...props} key={shop.id} />
      ))}
    </List>
  );
}
