import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { updateState } from "../../reducers/mainReducer";
import { API_URLS } from "../../Constants";

export function CategoryForm() {
  const categories = useSelector((state) => state.main.categories);
  const { categoryId } = useParams();
  const dispatch = useDispatch();

  const [selectedCategory, setSelectedCategory] = React.useState(null);
  const [description, setDescription] = React.useState("");
  const [parent, setParent] = React.useState(null);
  const [name, setName] = React.useState("");

  React.useEffect(() => {
    const category = categories.find((c) => c.id == categoryId) ?? null;
    setSelectedCategory(category);
    if (category === null) {
      setDescription("");
      setParent(null);
      setName("");
    } else {
      const parent_ = categories.find((c) => c.id == category.parent) ?? null;
      setParent(parent_ ? { ...parent_, label: parent_.name } : null);
      setDescription(category.description);
      setName(category.name);
    }
  }, [categoryId, categories]);

  const submitHandler = (method, url) => {
    const data = {
      name,
      description,
      parent: parent?.id || null,
    };
    axios({ method, url, data })
      .then((data) => {
        if (method === "post") {
          dispatch(
            updateState({
              categories: [...categories, data.data],
              message: { message: "Category created", severity: "success" },
            }),
          );
        } else if (method === "put") {
          const newCategories = categories.map((c) =>
            c.id === data.data.id ? data.data : c,
          );
          dispatch(
            updateState({
              categories: newCategories,
              message: { message: "Category updated", severity: "success" },
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
          options={categories
            .filter((c) => c.id != categoryId)
            .map((c) => ({ ...c, label: c.name }))}
          disabled={categories.length === 0}
          onChange={(_, v) => setParent(v)}
          value={parent}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Parent category"
              color={
                selectedCategory !== null &&
                selectedCategory.parent !== parent?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedCategory !== null &&
                selectedCategory.parent !== parent?.id
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
