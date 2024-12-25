import { useParams, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import axios from "axios";
import React from "react";

import Container from "@mui/material/Container";

import { FormTextField, FormActions, Form } from "../../components/form";
import { PagesURLs, APIResponseType, API_URLS } from "../../Constants";
import { setMessage } from "../../reducers/mainReducer";
import { CategoryType } from "../categoryPage/types";
import { ShopAddressType, ShopType } from "./types";

export function AddressForm(props: {
  selectedShop: ShopType<CategoryType<number>> | null;
  setAddresses: React.Dispatch<React.SetStateAction<ShopAddressType<number>[]>>;
  addresses: ShopAddressType<number>[];
}) {
  const { addressId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [selectedAddress, setSelectedAddress] =
    React.useState<ShopAddressType<number> | null>(null);
  const [localName, setLocalName] = React.useState<string>("");
  const [address, setAddress] = React.useState<string>("");

  const resetState = () => {
    setSelectedAddress(null);
    setLocalName("");
    setAddress("");
  };

  React.useEffect(() => {
    if (addressId === undefined) {
      resetState();
      return;
    }
    axios
      .get(`${API_URLS.Address}${addressId}/`)
      .then((data: APIResponseType<ShopAddressType<number>>) => {
        setLocalName(data.data.local_name);
        setAddress(data.data.address);
        setSelectedAddress(data.data);
      })
      .catch(() => resetState());
  }, [addressId]);

  const submitHandler = (method: "post" | "put", url: string) => {
    const data = {
      address,
      local_name: localName,
      shop: props.selectedShop!.id,
    };
    axios({ method, url, data })
      .then((data: APIResponseType<ShopAddressType<number>>) => {
        if (method === "post") {
          props.setAddresses([...props.addresses, data.data]);
          dispatch(
            setMessage({
              message: "New shop branch created",
              severity: "success",
            }),
          );
          navigate(
            `${PagesURLs.Shop}${props.selectedShop!.id}/${PagesURLs.Address}/${
              data.data.id
            }`,
          );
        } else if (method === "put") {
          const newAddresses = props.addresses.map((a) =>
            a.id === data.data.id ? data.data : a,
          );
          props.setAddresses(newAddresses);
          dispatch(
            setMessage({ message: "Shop branch updated", severity: "success" }),
          );
        }
      })
      .catch((e) => {
        dispatch(setMessage({ message: e.respose.data, severity: "error" }));
      });
  };

  if (props.selectedShop === null) return null;
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
