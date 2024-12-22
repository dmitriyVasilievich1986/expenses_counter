import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router";
import axios from "axios";
import React from "react";

import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Fab from "@mui/material/Fab";

import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";

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
      <Paper elevation={4} sx={{ p: 2 }}>
        <Typography variant="h5" align="center" sx={{ mb: 3 }}>
          Shop Branch Form
        </Typography>
        <Stack spacing={2}>
          <TextField
            onChange={(e) => setLocalName(e.target.value)}
            label="Shop local name"
            value={localName}
            fullWidth
            color={
              selectedAddress?.local_name &&
              selectedAddress?.local_name !== localName
                ? "warning"
                : "primary"
            }
            focused={
              selectedAddress?.local_name &&
              selectedAddress?.local_name !== localName
                ? true
                : undefined
            }
          />
          <TextField
            onChange={(e) => setAddress(e.target.value)}
            label="Shop address"
            value={address}
            fullWidth
            color={
              selectedAddress?.address && selectedAddress?.address !== address
                ? "warning"
                : "primary"
            }
            focused={
              selectedAddress?.address && selectedAddress?.address !== address
                ? true
                : undefined
            }
          />
        </Stack>
        <Box sx={{ display: "flex", justifyContent: "end", mt: 2 }}>
          <Stack spacing={2} direction="row">
            <Fab
              color="secondary"
              aria-label="EditIcon"
              onClick={(_) =>
                submitHandler("put", `${API_URLS.Address}${addressId}/`)
              }
              disabled={selectedAddress === null}
            >
              <EditIcon />
            </Fab>
            <Fab
              color="primary"
              aria-label="add"
              onClick={(_) => submitHandler("post", API_URLS.Address)}
            >
              <AddIcon />
            </Fab>
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}
