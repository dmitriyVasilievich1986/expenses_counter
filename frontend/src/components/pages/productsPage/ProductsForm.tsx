import { useNavigate, useParams } from "react-router";
import { useDispatch } from "react-redux";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { APIResponseType, PagesURLs, API_URLS } from "../../Constants";
import { CategoryTypeNumber } from "../categoryPage/types";
import { setMessage } from "../../reducers/mainReducer";
import { ProductTypeDetailed } from "./types";

export function ProductsForm(props: {
  products: ProductTypeDetailed[];
  setProducts: React.Dispatch<React.SetStateAction<ProductTypeDetailed[]>>;
}) {
  const { productId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [selectedProduct, setSelectedProduct] =
    React.useState<ProductTypeDetailed | null>(null);
  const [categories, setCategories] = React.useState<CategoryTypeNumber[]>([]);
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
  }, [productId, props.products]);

  React.useEffect(() => {
    axios
      .get(API_URLS.Category)
      .then((data: APIResponseType<CategoryTypeNumber[]>) => {
        setCategories(data.data);
      });
  }, []);

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
          props.setProducts([...props.products, data.data]);
          navigate(`${PagesURLs.Product}/${data.data.id}`);
        } else if (method === "put") {
          const newProducts = props.products.map((p) =>
            p.id === data.data.id ? data.data : p,
          );
          dispatch(setMessage({ message: "Product updated" }));
          props.setProducts(newProducts);
        }
      })
      .catch((e) => {
        console.log(e);
        dispatch(setMessage({ message: "error", severity: "error" }));
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
          disabled={categories.length === 0}
          options={categories}
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
