import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router";
import axios from "axios";
import React from "react";

import Container from "@mui/material/Container";

import { FormTextField, FormActions, Form } from "../../components/form";
import { MainReducerType, ShopAddressType } from "../../reducers/types";
import { updateState } from "../../reducers/mainReducer";
import { API_URLS } from "../../Constants";

export function AddressForm() {
  const addresses = useSelector(
    (state: MainReducerType) => state.main.addresses,
  );
  const shops = useSelector((state: MainReducerType) => state.main.shops);
  const { addressId, shopId } = useParams();
  const dispatch = useDispatch();

  const [selectedAddress, setSelectedAddress] = React.useState(null);
  const [selectedShop, setSelectedShop] = React.useState(null);
  const [localName, setLocalName] = React.useState("");
  const [address, setAddress] = React.useState("");

  React.useEffect(() => {
    const shop = shops.find((s) => s.id === parseInt(shopId)) ?? null;
    setSelectedShop(shop);
  }, [shops, shopId]);

  React.useEffect(() => {
    const address = addresses.find((a) => a.id === parseInt(addressId)) ?? null;
    setSelectedAddress(address);
    if (address === null) {
      setLocalName("");
      setAddress("");
    } else {
      setLocalName(address.local_name);
      setAddress(address.address);
    }
  }, [addresses, addressId]);

  const submitHandler = (method: "post" | "put", url: string) => {
    const data = {
      address,
      local_name: localName,
      shop: selectedShop!.id,
    };
    axios({ method, url, data })
      .then((data) => {
        if (method === "post") {
          dispatch(
            updateState({
              addresses: [...addresses, data.data as ShopAddressType],
              message: {
                message: "New shop branch created",
                severity: "success",
              },
            }),
          );
        } else if (method === "put") {
          const newAddress = addresses.map((a) =>
            a.id === data.data.id ? data.data : a,
          );
          dispatch(
            updateState({
              addresses: newAddress,
              message: { message: "Shop branch updated", severity: "success" },
            }),
          );
        }
      })
      .catch((e) => {
        updateState({
          message: { message: e.respose.data, severity: "error" },
        });
      });
  };

  if (selectedShop === null) return null;
  return (
    <Container maxWidth="lg">
      <Form title="Shop Branch Form">
        <FormTextField
          isChanged={
            selectedAddress !== null && selectedAddress.local_name !== localName
          }
          onChange={setLocalName}
          label="Shop local name"
          value={localName}
        />
        <FormTextField
          isChanged={
            selectedAddress !== null && selectedAddress.address !== address
          }
          onChange={setAddress}
          label="Shop address"
          value={address}
        />
        <FormActions
          disabledEdit={selectedAddress === null}
          submitHandler={submitHandler}
          url={API_URLS.Address}
          objectId={addressId}
        />
      </Form>
    </Container>
  );
}
