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
  updateCategoriy,
  addCategories,
  setCategories,
} from "../../reducers/mainReducer";

import { CategoryTypeNumber, CategoryTypeDetailed } from "./types";
import { mainSelectorType } from "../../reducers/types";

export function CategoryForm() {
  const isLoading = useSelector(
    (state: mainSelectorType) => state.main.isLoading,
  );
  const categories = useSelector(
    (state: mainSelectorType) => state.main.categories,
  );

  const navigate = useNavigateWithParams();
  const { categoryId } = useParams();
  const dispatch = useDispatch();
  const api = new API();

  const [selectedCategory, setSelectedCategory] =
    useState<CategoryTypeDetailed | null>(null);
  const [parent, setParent] = useState<CategoryTypeNumber | null>(null);
  const [description, setDescription] = useState<string>("");
  const [name, setName] = useState<string>("");

  const resetState = (data?: CategoryTypeDetailed) => {
    setDescription(data?.description ?? "");
    setSelectedCategory(data ?? null);
    setParent(data?.parent ?? null);
    setName(data?.name ?? "");
  };

  const getCurrentData = () => {
    api.send<CategoryTypeDetailed>({
      url: `${APIs.Category}${categoryId}/`,
      onSuccess: resetState,
      onFail: resetState,
    });
  };

  useEffect(() => {
    if (categoryId === undefined) resetState();
    else getCurrentData();
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
        if (method === Methods.post) {
          dispatch(addCategories([data]));
          navigate(`${PagesURLs.Category}${data.id}`);
        } else {
          dispatch(updateCategoriy(data));
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
