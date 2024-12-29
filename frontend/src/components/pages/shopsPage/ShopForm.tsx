import { useParams, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { PagesURLs, APIResponseType, API_URLS } from "../../Constants";
import { ShopTypeNumber, ShopTypeDetailed } from "./types";
import { CategoryTypeNumber } from "../categoryPage/types";
import { setMessage } from "../../reducers/mainReducer";

export function ShopForm(props: {
  setSelectedShop: React.Dispatch<
    React.SetStateAction<ShopTypeDetailed | null>
  >;
  setShops: React.Dispatch<React.SetStateAction<ShopTypeNumber[]>>;
  selectedShop: ShopTypeDetailed | null;
  shops: ShopTypeNumber[];
}) {
  const { shopId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [category, setCategory] = React.useState<CategoryTypeNumber | null>(
    null,
  );
  const [categories, setCategories] = React.useState<CategoryTypeNumber[]>([]);
  const [description, setDescription] = React.useState<string>("");
  const [iconURL, setIconURL] = React.useState<string>("");
  const [name, setName] = React.useState<string>("");

  React.useEffect(() => {
    axios
      .get(API_URLS.Category)
      .then((data: APIResponseType<CategoryTypeNumber[]>) => {
        setCategories(data.data);
      });
  }, []);

  const getCategoryWithLabel = (
    category: CategoryTypeNumber,
    label?: string,
  ): string => {
    const newLabel = label ?? category.name;
    if (category.parent === null || categories.length === 0) {
      return newLabel;
    }
    const parentCategory = categories.find(
      (c) => c.id === category.parent,
    ) as CategoryTypeNumber;
    return getCategoryWithLabel(
      parentCategory,
      `${parentCategory?.name} > ${newLabel}`,
    );
  };

  const resetState = () => {
    props.setSelectedShop(null);
    setDescription("");
    setCategory(null);
    setIconURL("");
    setName("");
  };

  React.useEffect(() => {
    if (shopId === undefined || categories.length === 0) {
      resetState();
      return;
    }
    axios
      .get(`${API_URLS.Shop}${shopId}/`)
      .then((data: APIResponseType<ShopTypeDetailed>) => {
        setCategory(data.data.category === null ? null : data.data.category);
        setDescription(data.data.description);
        setIconURL(data.data.icon ?? "");
        props.setSelectedShop(data.data);
        setName(data.data.name);
      })
      .catch(() => resetState());
  }, [categories, shopId]);

  const submitHandler = (method: "post" | "put", url: string) => {
    const data = {
      name,
      description,
      icon: iconURL || null,
      category: category?.id || null,
    };
    axios({ method, url, data })
      .then((data: APIResponseType<ShopTypeNumber>) => {
        if (method === "post") {
          props.setShops([...props.shops, data.data]);
          dispatch(
            setMessage({ message: "Shop created", severity: "success" }),
          );
          navigate(`${PagesURLs.Shop}${data.data.id}`);
        } else if (method === "put") {
          const newShops = props.shops.map((s) =>
            s.id === data.data.id ? data.data : s,
          );
          props.setShops(newShops);
          dispatch(
            setMessage({ message: "Shop updated", severity: "success" }),
          );
        }
      })
      .catch((e) => {
        dispatch(setMessage({ message: e.respose.data, severity: "error" }));
      });
  };

  return (
    <Container maxWidth="lg">
      <Form title="Shop form">
        <FormTextField
          isChanged={
            props.selectedShop !== null && props.selectedShop.name !== name
          }
          onChange={setName}
          label="Shop name"
          value={name}
        />
        <FormTextField
          label="Shop logo URL"
          onChange={setIconURL}
          value={iconURL}
          isChanged={
            props.selectedShop !== null &&
            (props.selectedShop.icon ?? "") !== iconURL
          }
        />
        <FormTextField
          onChange={setDescription}
          label="Shop description"
          value={description}
          isChanged={
            props.selectedShop !== null &&
            props.selectedShop.description !== description
          }
        />
        <Autocomplete
          getOptionLabel={(option) => getCategoryWithLabel(option)}
          onChange={(_, v) => setCategory(v)}
          disabled={categories.length === 0}
          options={categories}
          value={category}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Category"
              color={
                props.selectedShop !== null &&
                props.selectedShop.category?.id !== category?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                props.selectedShop !== null &&
                props.selectedShop.category?.id !== category?.id
                  ? true
                  : undefined
              }
            />
          )}
        />
        <FormActions
          disabledEdit={props.selectedShop === null}
          submitHandler={submitHandler}
          url={API_URLS.Shop}
          objectId={shopId}
        />
      </Form>
    </Container>
  );
}
