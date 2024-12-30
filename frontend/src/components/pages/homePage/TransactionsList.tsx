import { useDispatch, useSelector } from "react-redux";
import React, { useEffect } from "react";

import Container from "@mui/material/Container";
import List from "@mui/material/List";

import { setAddresses } from "../../reducers/mainReducer";
import { APIs, API } from "../../api";
import { ShopCard } from "./ShopCard";

import { ShopAddressTypeNumber } from "../shopsPage/types";
import { mainSelectorType } from "../../reducers/types";

export function TransactionsList() {
  const transactions = useSelector(
    (state: mainSelectorType) => state.main.transactions,
  );
  const addresses = useSelector(
    (state: mainSelectorType) => state.main.addresses,
  );

  const dispatch = useDispatch();
  const api = new API();

  const filteredAddresses: { [key in number]: ShopAddressTypeNumber } = {};
  transactions.forEach((t) => {
    filteredAddresses[t.address.id as number] = t.address;
  });

  useEffect(() => {
    if (addresses.length !== 0) return;
    api.send<ShopAddressTypeNumber>({
      url: APIs.Address,
      onSuccess: (data) => dispatch(setAddresses(data)),
    });
  }, [addresses]);

  return (
    <Container sx={{ display: "flex", justifyContent: "center" }}>
      <List sx={{ width: "100%", maxWidth: "700px" }}>
        {Object.values(filteredAddresses).map((a) => (
          <ShopCard
            key={a.id}
            address={addresses.find((ad) => ad.id === a.id) ?? a}
            transactions={transactions.filter((t) => t.address.id === a.id)}
          />
        ))}
      </List>
    </Container>
  );
}
