import * as React from "react";
import axios from "axios";

import Stack from "@mui/material/Stack";
import Grid from "@mui/material/Grid2";
import Box from "@mui/material/Box";

import {
  ShopTypeNumber,
  ShopTypeDetailed,
  ShopAddressTypeNumber,
} from "./types";
import { APIResponseType, API_URLS } from "../../Constants";
import { AddressForm } from "./AddressForm";
import { ShopsList } from "./ShopsList";
import { ShopForm } from "./ShopForm";

export function ShopsPage() {
  const [selectedShop, setSelectedShop] =
    React.useState<ShopTypeDetailed | null>(null);
  const [addresses, setAddresses] = React.useState<ShopAddressTypeNumber[]>([]);
  const [shops, setShops] = React.useState<ShopTypeNumber[]>([]);

  React.useEffect(() => {
    axios.get(API_URLS.Shop).then((data: APIResponseType<ShopTypeNumber[]>) => {
      setShops(data.data);
    });
    axios
      .get(API_URLS.Address)
      .then((data: APIResponseType<ShopAddressTypeNumber[]>) => {
        setAddresses(data.data);
      });
  }, []);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 4, md: 3 }}>
          <ShopsList shops={shops} addresses={addresses} />
        </Grid>
        <Grid size={{ xs: 12, sm: 8, md: 6 }}>
          <Stack spacing={2}>
            <ShopForm
              shops={shops}
              setShops={setShops}
              selectedShop={selectedShop}
              setSelectedShop={setSelectedShop}
            />
            <AddressForm
              selectedShop={selectedShop}
              addresses={addresses}
              setAddresses={setAddresses}
            />
          </Stack>
        </Grid>
        <Grid size={{ xs: 12, sm: 12, md: 3 }}></Grid>
      </Grid>
    </Box>
  );
}
