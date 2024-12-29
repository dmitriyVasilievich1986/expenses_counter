import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { updateCategoriy, addCategories } from "../../reducers/mainReducer";
import { FormTextField, FormActions, Form } from "../../components/form";
import { useNavigateWithParams } from "../../components/link";
import { Methods, APIs, API } from "../../api";
import { PagesURLs } from "../../Constants";

import { CategoryTypeNumber, CategoryTypeDetailed } from "./types";
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
  const api = new API();

  const [selectedCategory, setSelectedCategory] =
    React.useState<CategoryTypeDetailed | null>(null);
  const [parent, setParent] = React.useState<CategoryTypeNumber | null>(null);
  const [description, setDescription] = React.useState<string>("");
  const [name, setName] = React.useState<string>("");

  const resetState = (data?: CategoryTypeDetailed) => {
    setDescription(data?.description ?? "");
    setSelectedCategory(data ?? null);
    setParent(data?.parent ?? null);
    setName(data?.name ?? "");
  };

  React.useEffect(() => {
    if (categoryId === undefined) {
      resetState();
      return;
    }
    api.send<CategoryTypeDetailed>({
      url: `${APIs.Category}${categoryId}/`,
      onSuccess: resetState,
      onFail: resetState,
    });
  }, [categoryId]);

  const submitHandler = (method: Methods.post | Methods.put, url: string) => {
    const data = {
      name,
      description,
      parent: parent && parent.id,
    };
    const messages = {
      [Methods.post]: "Category created",
      [Methods.put]: "Category updated",
    };
    api.send<CategoryTypeNumber>({
      method,
      url,
      data,
      successMessage: { message: messages[method] },
      onSuccess: (data) => {
        if (method === "post") {
          dispatch(addCategories([data]));
          navigate(`${PagesURLs.Category}${data.id}`);
        } else if (method === "put") {
          dispatch(updateCategoriy(data));
          const parentCategory = categories.find((p) => p.id === data.parent);
          resetState({ ...data, parent: parentCategory });
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
          objectId={categoryId}
          url={APIs.Category}
        />
      </Form>
    </Container>
  );
}
