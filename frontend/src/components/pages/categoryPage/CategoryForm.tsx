import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import {
  updateCategoriy,
  addCategories,
  setIsLoading,
  setMessage,
} from "../../reducers/mainReducer";
import { FormTextField, FormActions, Form } from "../../components/form";
import { PagesURLs, APIResponseType, API_URLS } from "../../Constants";
import { CategoryTypeNumber, CategoryTypeDetailed } from "./types";
import { useNavigateWithParams } from "../../components/link";
import { mainStateType } from "../../reducers/types";

export function CategoryForm() {
  const isLoading = useSelector(
    (state: { main: mainStateType }) => state.main.isLoading,
  );
  const categories = useSelector(
    (state: { main: mainStateType }) => state.main.categories,
  );

  const navigate = useNavigateWithParams();
  const { categoryId } = useParams();
  const dispatch = useDispatch();

  const [selectedCategory, setSelectedCategory] =
    React.useState<CategoryTypeDetailed | null>(null);
  const [parent, setParent] = React.useState<CategoryTypeNumber | null>(null);
  const [description, setDescription] = React.useState<string>("");
  const [name, setName] = React.useState<string>("");

  const resetState = () => {
    setSelectedCategory(null);
    setDescription("");
    setParent(null);
    setName("");
  };

  React.useEffect(() => {
    if (categoryId === undefined) {
      resetState();
      return;
    }
    axios
      .get(`${API_URLS.Category}${categoryId}/`)
      .then((data: APIResponseType<CategoryTypeDetailed>) => {
        setParent(data.data.parent === null ? null : data.data.parent);
        setDescription(data.data.description);
        setSelectedCategory(data.data);
        setName(data.data.name);
      })
      .catch(() => resetState());
  }, [categoryId]);

  const submitHandler = (method: "post" | "put", url: string) => {
    const data = {
      name,
      description,
      parent: parent === null ? null : parent.id,
    };
    axios({ method, url, data })
      .then((data: APIResponseType<CategoryTypeNumber>) => {
        if (method === "post") {
          dispatch(addCategories([data.data]));
          dispatch(setMessage({ message: "Category created" }));
          navigate(`${PagesURLs.Category}${data.data.id}`);
        } else if (method === "put") {
          dispatch(updateCategoriy(data.data));
          dispatch(setMessage({ message: "Category updated" }));
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
      <Form title="Category form">
        <FormTextField
          isChanged={
            selectedCategory !== null && selectedCategory.name !== name
          }
          label="Category name"
          onChange={setName}
          value={name}
        />
        <FormTextField
          isChanged={
            selectedCategory !== null &&
            selectedCategory.description !== description
          }
          label="Category description"
          onChange={setDescription}
          value={description}
        />
        <Autocomplete
          options={categories.filter(
            (c) => categoryId === undefined || c.id !== parseInt(categoryId),
          )}
          getOptionLabel={(option) => option.name}
          onChange={(_, v) => setParent(v)}
          onOpen={loadCategories}
          loading={isLoading}
          value={parent}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Parent category"
              color={
                selectedCategory !== null &&
                selectedCategory.parent?.id !== parent?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedCategory !== null &&
                selectedCategory.parent?.id !== parent?.id
                  ? true
                  : undefined
              }
            />
          )}
        />
        <FormActions
          disabledEdit={categoryId === undefined}
          submitHandler={submitHandler}
          url={API_URLS.Category}
          objectId={categoryId}
        />
      </Form>
    </Container>
  );
}
