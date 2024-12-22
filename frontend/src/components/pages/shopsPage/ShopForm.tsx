import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Fab from "@mui/material/Fab";

import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";

import { MainReducerType, CategoryType, ShopType } from "../../reducers/types";
import { updateState } from "../../reducers/mainReducer";
import { API_URLS } from "../../Constants";

export function ShopForm() {
  const categories = useSelector(
    (state: MainReducerType) => state.main.categories,
  );
  const shops = useSelector((state: MainReducerType) => state.main.shops);
  const { shopId } = useParams();
  const dispatch = useDispatch();

  const [selectedShop, setSelectedShop] = React.useState(null);
  const [description, setDescription] = React.useState("");
  const [category, setCategory] = React.useState(null);
  const [name, setName] = React.useState("");

  const getCategoryWithLabel = (category: CategoryType, label?: string) => {
    const newLabel = label ?? category.name;
    if (category.parent === null) {
      return newLabel;
    }
    const parentCategory = categories.find((c) => c.id === category.parent);
    return getCategoryWithLabel(
      parentCategory,
      `${parentCategory?.name} > ${newLabel}`,
    );
  };

  React.useEffect(() => {
    const shop = shops.find((s) => s.id === parseInt(shopId));
    if (shop) {
      const category = categories.find((c) => c.id === shop.category) ?? null;
      setCategory(
        category
          ? { ...category, label: getCategoryWithLabel(category) }
          : null,
      );
      setDescription(shop.description);
      setSelectedShop(shop);
      setName(shop.name);
    } else {
      setSelectedShop(null);
      setDescription("");
      setCategory(null);
      setName("");
    }
  }, [shops, shopId]);

  const submitHandler = (method: "post" | "put", url: string) => {
    const data = {
      name,
      description,
      category: category?.id || null,
    };
    axios({ method, url, data })
      .then((data) => {
        if (method === "post") {
          dispatch(
            updateState({
              shops: [...shops, data.data as ShopType],
              message: { message: "Shop created", severity: "success" },
            }),
          );
        } else if (method === "put") {
          const newShop = shops.map((s) =>
            s.id === data.data.id ? data.data : s,
          );
          dispatch(
            updateState({
              shops: newShop,
              message: { message: "Shop updated", severity: "success" },
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

  return (
    <Container maxWidth="lg">
      <Paper elevation={4} sx={{ p: 2 }}>
        <Typography variant="h5" align="center" sx={{ mb: 3 }}>
          Shop Form
        </Typography>
        <Stack spacing={2}>
          <TextField
            onChange={(e) => setName(e.target.value)}
            label="Shop name"
            value={name}
            fullWidth
            color={
              selectedShop?.name && selectedShop?.name !== name
                ? "warning"
                : "primary"
            }
            focused={
              selectedShop?.name && selectedShop?.name !== name
                ? true
                : undefined
            }
          />
          <TextField
            onChange={(e) => setDescription(e.target.value)}
            label="Shop description"
            value={description}
            fullWidth
            color={
              selectedShop?.description &&
              selectedShop?.description !== description
                ? "warning"
                : "primary"
            }
            focused={
              selectedShop?.description &&
              selectedShop?.description !== description
                ? true
                : undefined
            }
          />
          <Autocomplete
            options={categories.map((c) => ({
              ...c,
              label: getCategoryWithLabel(c),
            }))}
            onChange={(_, v) => setCategory(v)}
            disabled={categories.length === 0}
            value={category}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Category"
                color={
                  selectedShop?.category &&
                  selectedShop?.category !== category?.id
                    ? "warning"
                    : "primary"
                }
                focused={
                  selectedShop?.category &&
                  selectedShop?.category !== category?.id
                    ? true
                    : undefined
                }
              />
            )}
          />
        </Stack>
        <Box sx={{ display: "flex", justifyContent: "end", mt: 2 }}>
          <Stack spacing={2} direction="row">
            <Fab
              color="secondary"
              aria-label="EditIcon"
              onClick={(_) =>
                submitHandler("put", `${API_URLS.Shop}${shopId}/`)
              }
              disabled={selectedShop === null}
            >
              <EditIcon />
            </Fab>
            <Fab
              color="primary"
              aria-label="add"
              onClick={(_) => submitHandler("post", API_URLS.Shop)}
            >
              <AddIcon />
            </Fab>
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}
