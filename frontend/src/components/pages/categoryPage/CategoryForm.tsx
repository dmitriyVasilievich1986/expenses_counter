import { useParams, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { PagesURLs, APIResponseType, API_URLS } from "../../Constants";
import { CategoryTypeNumber, CategoryTypeDetailed } from "./types";
import { setMessage } from "../../reducers/mainReducer";

export function CategoryForm(props: {
  setCategories: (categories: CategoryTypeNumber[]) => void;
  categories: CategoryTypeNumber[];
}) {
  const { categoryId } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();

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
  }, [categoryId, props.categories]);

  const submitHandler = (method: "post" | "put", url: string) => {
    const data = {
      name,
      description,
      parent: parent === null ? null : parent.id,
    };
    axios({ method, url, data })
      .then((data: APIResponseType<CategoryTypeNumber>) => {
        if (method === "post") {
          props.setCategories([...props.categories, data.data]);
          dispatch(
            setMessage({ message: "Category created", severity: "success" }),
          );
          navigate(`${PagesURLs.Category}${data.data.id}`);
        } else if (method === "put") {
          const newCategories = props.categories.map((c) =>
            c.id === data.data.id ? data.data : c,
          );
          dispatch(
            setMessage({ message: "Category updated", severity: "success" }),
          );
          props.setCategories(newCategories);
        }
      })
      .catch((e) => {
        dispatch(setMessage({ message: e.respose.data, severity: "error" }));
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
          options={props.categories.filter(
            (c) => categoryId !== undefined && c.id !== parseInt(categoryId),
          )}
          getOptionLabel={(option) => option.name}
          disabled={props.categories.length === 0}
          onChange={(_, v) => setParent(v)}
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
