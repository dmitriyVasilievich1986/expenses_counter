import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { useNavigateWithParams } from "../../components/link";
import { CategoryTypeNumber } from "../categoryPage/types";
import { mainStateType } from "../../reducers/types";
import { ProductTypeDetailed } from "./types";
import { Methods, API, APIs } from "../../api";
import { PagesURLs } from "../../Constants";
import {
  updateProduct,
  addCategories,
  addProducts,
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
  const api = new API();

  const [selectedProduct, setSelectedProduct] =
    React.useState<ProductTypeDetailed | null>(null);
  const [subCategory, setSubCategory] =
    React.useState<CategoryTypeNumber | null>(null);
  const [description, setDescription] = React.useState<string>("");
  const [name, setName] = React.useState<string>("");

  const resetState = (data?: ProductTypeDetailed) => {
    setSubCategory(data?.sub_category ?? null);
    setDescription(data?.description ?? "");
    setSelectedProduct(data ?? null);
    setName(data?.name ?? "");
  };

  React.useEffect(() => {
    if (productId === undefined) {
      resetState();
      return;
    }
    api.send<ProductTypeDetailed>({
      url: `${APIs.Product}${productId}/`,
      onFail: resetState,
      onSuccess: resetState,
    });
  }, [productId]);

  const submitHandler = (method: Methods.post | Methods.put, url: string) => {
    const data = {
      name,
      description,
      sub_category: subCategory!.id,
    };
    const messages = {
      [Methods.post]: "Product created",
      [Methods.put]: "Product updated",
    };
    api.send<ProductTypeDetailed>({
      url,
      method,
      data,
      successMessage: { message: messages[method] },
      onSuccess: (data) => {
        if (method === Methods.post) {
          dispatch(addProducts([data]));
          navigate(`${PagesURLs.Product}/${data.id}`);
        } else {
          dispatch(updateProduct(data));
          resetState(data);
        }
      },
    });
  };

  const loadCategories = () => {
    if (categories.length !== 0 || isLoading) return;
    api.send<CategoryTypeNumber[]>({
      url: APIs.Category,
      onSuccess: (data) => dispatch(addCategories(data)),
    });
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
          objectId={productId}
          url={APIs.Product}
        />
      </Form>
    </Container>
  );
}
