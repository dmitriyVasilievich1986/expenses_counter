import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { MainReducerType, CategoryType, ShopType } from "../../reducers/types";
import { FormTextField, FormActions, Form } from "../../components/form";
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
    const shop = shops.find((s) => s.id === parseInt(shopId)) ?? null;
    setSelectedShop(shop);
    if (shop) {
      const category = categories.find((c) => c.id === shop.category) ?? null;
      setCategory(
        category
          ? { ...category, label: getCategoryWithLabel(category) }
          : null,
      );
      setDescription(shop.description);
      setName(shop.name);
    } else {
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
      <Form title="Shop form">
        <FormTextField
          isChanged={selectedShop !== null && selectedShop.name !== name}
          onChange={setName}
          label="Shop name"
          value={name}
        />
        <FormTextField
          onChange={setDescription}
          label="Shop description"
          value={description}
          isChanged={
            selectedShop !== null && selectedShop.description !== description
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
                selectedShop !== null && selectedShop.category !== category?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedShop !== null && selectedShop.category !== category?.id
                  ? true
                  : undefined
              }
            />
          )}
        />
        <FormActions
          disabledEdit={selectedShop === null}
          submitHandler={submitHandler}
          url={API_URLS.Shop}
          objectId={shopId}
        />
      </Form>
    </Container>
  );
}
