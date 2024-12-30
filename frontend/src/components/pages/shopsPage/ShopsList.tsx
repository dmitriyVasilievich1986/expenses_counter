import { useDispatch, useSelector } from "react-redux";
import React, { useEffect } from "react";

import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { setAddresses, setShops } from "../../reducers/mainReducer";
import { LinkBox } from "../../components/link";
import { PagesURLs } from "../../Constants";
import { APIs, API } from "../../api";

import { ShopTypeNumber, ShopAddressTypeNumber } from "./types";
import { mainSelectorType } from "../../reducers/types";

function Addresses(props: { addresses: ShopAddressTypeNumber[] }) {
  if (props.addresses.length === 0) return null;
  return (
    <List sx={{ ml: 4 }}>
      {props.addresses.map((a) => (
        <LinkBox
          to={`${PagesURLs.Shop}/${a.shop}/${PagesURLs.Address}/${a.id}`}
          key={a.id}
        >
          <Typography variant="subtitle1" sx={{ m: 0 }}>
            {a.local_name}
          </Typography>
          <Typography variant="caption" sx={{ m: 0 }}>
            {a.address}
          </Typography>
        </LinkBox>
      ))}
    </List>
  );
}

function Shop(props: { shop: ShopTypeNumber; shops: ShopTypeNumber[] }) {
  const addresses = useSelector(
    (state: mainSelectorType) => state.main.addresses,
  );

  const dispatch = useDispatch();
  const api = new API();

  useEffect(() => {
    if (addresses.length !== 0) return;
    api.send<ShopAddressTypeNumber[]>({
      url: APIs.Address,
      onSuccess: (data) => dispatch(setAddresses(data)),
    });
  }, [addresses]);

  const filteredAddresses = addresses.filter((a) => a.shop === props.shop.id);
  return (
    <Box>
      <LinkBox to={`${PagesURLs.Shop}/${props.shop.id}`}>
        {props.shop.name}
      </LinkBox>
      <Addresses addresses={filteredAddresses} />
    </Box>
  );
}

export function ShopsList() {
  const shops = useSelector((state: mainSelectorType) => state.main.shops);
  const dispatch = useDispatch();
  const api = new API();

  useEffect(() => {
    if (shops.length !== 0) return;
    api.send<ShopTypeNumber[]>({
      url: APIs.Shop,
      onSuccess: (data) => dispatch(setShops(data)),
    });
  }, [shops]);

  if (shops.length === 0) return null;
  return (
    <List sx={{ pl: 2 }}>
      {shops.map((shop) => (
        <Shop shop={shop} shops={shops} key={shop.id} />
      ))}
    </List>
  );
}
