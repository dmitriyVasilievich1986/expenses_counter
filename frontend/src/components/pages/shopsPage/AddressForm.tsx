import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useDispatch } from "react-redux";

import Container from "@mui/material/Container";

import { addAddresses, updateAddress } from "../../reducers/mainReducer";
import { FormTextField, FormActions, Form } from "../../components/form";
import { useNavigateWithParams } from "../../components/link";
import { Methods, APIs, API } from "../../api";
import { PagesURLs } from "../../Constants";

import { ShopAddressTypeNumber } from "./types";

export function AddressForm() {
  const navigate = useNavigateWithParams();
  const { addressId } = useParams();
  const { shopId } = useParams();
  const dispatch = useDispatch();
  const api = new API();

  const [selectedAddress, setSelectedAddress] =
    useState<ShopAddressTypeNumber | null>(null);
  const [localName, setLocalName] = useState<string>("");
  const [address, setAddress] = useState<string>("");

  const resetState = (data?: ShopAddressTypeNumber) => {
    setLocalName(data?.local_name ?? "");
    setSelectedAddress(data ?? null);
    setAddress(data?.address ?? "");
  };

  const getCurrentData = () => {
    api.send<ShopAddressTypeNumber>({
      url: `${APIs.Address}${addressId}/`,
      onSuccess: resetState,
      onFail: resetState,
    });
  };

  useEffect(() => {
    if (addressId === undefined) resetState();
    else getCurrentData();
  }, [addressId]);

  const submitHandler = (method: Methods.post | Methods.put, url: string) => {
    const data = {
      address,
      local_name: localName,
      shop: shopId as string,
    };
    const messages = {
      [Methods.post]: "New shop branch created",
      [Methods.put]: "Shop branch updated",
    };
    api.send<ShopAddressTypeNumber>({
      method,
      url,
      data,
      successMessage: { message: messages[method] },
      onSuccess: (data) => {
        if (method === Methods.post) {
          dispatch(addAddresses(data));
          navigate(
            `${PagesURLs.Shop}${shopId}/${PagesURLs.Address}/${data.id}`,
          );
        } else {
          dispatch(updateAddress(data));
          getCurrentData();
        }
      },
    });
  };

  if (!shopId) return null;
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
          objectId={addressId}
          url={APIs.Address}
        />
      </Form>
    </Container>
  );
}
