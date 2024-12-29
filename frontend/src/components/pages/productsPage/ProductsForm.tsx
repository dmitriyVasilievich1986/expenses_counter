import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { APIResponseType, PagesURLs, API_URLS } from "../../Constants";
import { useNavigateWithParams } from "../../components/link";
import { CategoryTypeNumber } from "../categoryPage/types";
import { mainStateType } from "../../reducers/types";
import { ProductTypeDetailed } from "./types";
import {
  updateProduct,
  setIsLoading,
  addProducts,
  addCategories,
  setMessage,
} from "../../reducers/mainReducer";

export function ProductsForm() {
  const isLoading = useSelector(
    (state: { main: mainStateType }) => state.main.isLoading,
  );
  const categories = useSelector(
    (state: { main: mainStateType }) => state.main.categories,
  );

  const navigate = useNavigateWithParams();
  const { productId } = useParams();
  const dispatch = useDispatch();

  const [selectedProduct, setSelectedProduct] =
    React.useState<ProductTypeDetailed | null>(null);
  const [subCategory, setSubCategory] =
    React.useState<CategoryTypeNumber | null>(null);
  const [description, setDescription] = React.useState<string>("");
  const [name, setName] = React.useState<string>("");

  const resetState = () => {
    setSelectedProduct(null);
    setSubCategory(null);
    setDescription("");
    setName("");
  };

  React.useEffect(() => {
    if (productId === undefined) {
      resetState();
      return;
    }
    axios
      .get(`${API_URLS.Product}${productId}/`)
      .then((data: APIResponseType<ProductTypeDetailed>) => {
        setSubCategory(data.data.sub_category);
        setDescription(data.data.description);
        setSelectedProduct(data.data);
        setName(data.data.name);
      })
      .catch(() => resetState());
  }, [productId]);

  const submitHandler = (method: "post" | "put", url: string) => {
    const data = {
      name,
      description,
      sub_category: subCategory!.id,
    };
    axios({ method, url, data })
      .then((data: APIResponseType<ProductTypeDetailed>) => {
        if (method === "post") {
          dispatch(setMessage({ message: "Product created" }));
          dispatch(addProducts([data.data]));
          navigate(`${PagesURLs.Product}/${data.data.id}`);
        } else if (method === "put") {
          dispatch(updateProduct(data.data));
          dispatch(setMessage({ message: "Product updated" }));
        }
      })
      .catch((e) => {
        console.log(e);
        dispatch(setMessage({ message: "error", severity: "error" }));
      });
  };

  const loadCategories = () => {
    if (categories.length !== 0 || isLoading) return;
    dispatch(setIsLoading(true));
    axios
      .get(API_URLS.Category)
      .then((data: APIResponseType<CategoryTypeNumber[]>) => {
        dispatch(addCategories(data.data));
      })
      .finally(() => dispatch(setIsLoading(false)));
  };

  return (
    <Container maxWidth="lg">
      <Form title="Product form">
        <FormTextField
          isChanged={selectedProduct !== null && selectedProduct.name !== name}
          label="Product name"
          onChange={setName}
          value={name}
        />
        <FormTextField
          isChanged={
            selectedProduct !== null &&
            selectedProduct.description !== description
          }
          label="Product description"
          onChange={setDescription}
          value={description}
        />
        <Autocomplete
          getOptionLabel={(option) => option.name}
          onChange={(_, v) => setSubCategory(v)}
          onOpen={loadCategories}
          options={categories}
          loading={isLoading}
          value={subCategory}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Product category"
              color={
                selectedProduct !== null &&
                selectedProduct.sub_category?.id !== subCategory?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedProduct !== null &&
                selectedProduct.sub_category?.id !== subCategory?.id
                  ? true
                  : undefined
              }
            />
          )}
        />
        <FormActions
          disabledEdit={productId === undefined}
          submitHandler={submitHandler}
          url={API_URLS.Product}
          objectId={productId}
        />
      </Form>
    </Container>
  );
}
