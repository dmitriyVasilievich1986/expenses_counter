import { useDispatch, useSelector } from "react-redux";
import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { useNavigateWithParams } from "../../components/link";
import { Methods, APIs, API } from "../../api";
import { PagesURLs } from "../../Constants";
import {
  setCategories,
  updateShop,
  addShops,
} from "../../reducers/mainReducer";

import { ShopTypeNumber, ShopTypeDetailed } from "./types";
import { CategoryTypeNumber } from "../categoryPage/types";
import { mainSelectorType } from "../../reducers/types";

export function ShopForm() {
  const navigate = useNavigateWithParams();
  const { shopId } = useParams();
  const dispatch = useDispatch();
  const api = new API();

  const isLoading = useSelector(
    (state: mainSelectorType) => state.main.isLoading,
  );
  const categories = useSelector(
    (state: mainSelectorType) => state.main.categories,
  );

  const [selectedShop, setSelectedShop] = useState<ShopTypeDetailed | null>(
    null,
  );
  const [category, setCategory] = useState<CategoryTypeNumber | null>(null);
  const [description, setDescription] = useState<string>("");
  const [iconURL, setIconURL] = useState<string>("");
  const [name, setName] = useState<string>("");

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

  const resetState = (data?: ShopTypeDetailed) => {
    setDescription(data?.description ?? "");
    setCategory(data?.category ?? null);
    setSelectedShop(data ?? null);
    setIconURL(data?.icon ?? "");
    setName(data?.name ?? "");
  };

  const getCurrentData = () => {
    api.send<ShopTypeDetailed>({
      url: `${APIs.Shop}${shopId}/`,
      onSuccess: resetState,
      onFail: resetState,
    });
  };

  useEffect(() => {
    if (shopId === undefined) resetState();
    else getCurrentData();
  }, [shopId]);

  const submitHandler = (method: Methods.post | Methods.put, url: string) => {
    const data = {
      name,
      description,
      icon: iconURL || null,
      category: category?.id || null,
    };
    const messages = {
      [Methods.post]: "Shop created",
      [Methods.put]: "Shop updated",
    };
    api.send<ShopTypeNumber>({
      method,
      url,
      data,
      successMessage: { message: messages[method] },
      onSuccess: (data) => {
        if (method === Methods.post) {
          dispatch(addShops([data]));
          navigate(`${PagesURLs.Shop}/${data.id}`);
        } else {
          dispatch(updateShop(data));
          getCurrentData();
        }
      },
    });
  };

  const loadCategories = () => {
    if (categories.length !== 0 || isLoading) return;
    api.send<CategoryTypeNumber[]>({
      url: APIs.Category,
      onSuccess: (data) => dispatch(setCategories(data)),
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
          label="Shop logo URL"
          onChange={setIconURL}
          value={iconURL}
          isChanged={
            selectedShop !== null && (selectedShop.icon ?? "") !== iconURL
          }
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
          getOptionLabel={(option) => getCategoryWithLabel(option)}
          getOptionKey={(option) => option.id as number}
          onChange={(_, v) => setCategory(v)}
          onOpen={loadCategories}
          options={categories}
          loading={isLoading}
          value={category}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Category"
              color={
                selectedShop !== null &&
                selectedShop.category?.id !== category?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedShop !== null &&
                selectedShop.category?.id !== category?.id
                  ? true
                  : undefined
              }
            />
          )}
        />
        <FormActions
          disabledEdit={selectedShop === null}
          submitHandler={submitHandler}
          objectId={shopId}
          url={APIs.Shop}
        />
      </Form>
    </Container>
  );
}
