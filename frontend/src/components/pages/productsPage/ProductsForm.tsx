import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { updateState } from "../../reducers/mainReducer";
import { MainReducerType } from "../../reducers/types";
import { API_URLS } from "../../Constants";

export function ProductsForm() {
  const categories = useSelector(
    (state: MainReducerType) => state.main.categories,
  );
  const products = useSelector((state: MainReducerType) => state.main.products);
  const { productId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [selectedProduct, setSelectedProduct] = React.useState(null);
  const [subCategory, setSubCategory] = React.useState(null);
  const [description, setDescription] = React.useState("");
  const [name, setName] = React.useState("");

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
      .then((data: APIResponseType<ProductType<CategoryType<number>>>) => {
        setSubCategory(
          data.data.sub_category === null
            ? null
            : { ...data.data.sub_category, label: data.data.sub_category.name },
        );
        setDescription(data.data.description);
        setSelectedProduct(data.data);
        setName(data.data.name);
      })
      .catch(() => resetState());
  }, [productId, props.products]);

  const submitHandler = (method: "post" | "put", url: string) => {
    const data = {
      name,
      description,
      sub_category: subCategory!.id,
    };
    axios({ method, url, data })
      .then((data) => {
        if (method === "post") {
          dispatch(
            updateState({
              products: [...products, data.data],
              message: { message: "Product created", severity: "success" },
            }),
          );
          navigate(`/create/product/${data.data.id}`);
        } else if (method === "put") {
          const newProduct = products.map((p) =>
            p.id === data.data.id ? data.data : p,
          );
          dispatch(
            updateState({
              products: newProduct,
              message: { message: "Product updated", severity: "success" },
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
          options={categories.map((c) => ({ ...c, label: c.name }))}
          disabled={categories.length === 0}
          onChange={(_, v) => setSubCategory(v)}
          value={subCategory}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Product category"
              color={
                selectedProduct !== null &&
                selectedProduct.sub_category !== subCategory?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedProduct !== null &&
                selectedProduct.sub_category !== subCategory?.id
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
