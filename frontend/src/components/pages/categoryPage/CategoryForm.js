import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router";
import axios from "axios";
import React from "react";

import Autocomplete from "@mui/material/Autocomplete";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Fab from "@mui/material/Fab";

import EditIcon from "@mui/icons-material/Edit";
import AddIcon from "@mui/icons-material/Add";

import { updateState } from "../../reducers/mainReducer";
import { API_URLS } from "../../Constants";

export function CategoryForm() {
  const categories = useSelector((state) => state.main.categories);
  const { categoryId } = useParams();
  const dispatch = useDispatch();

  const [description, setDescription] = React.useState("");
  const [parent, setParent] = React.useState(null);
  const [name, setName] = React.useState("");

  React.useEffect(() => {
    const selectedCategory = categories.find((c) => c.id == categoryId);
    if (selectedCategory) {
      setName(selectedCategory.name);
      setDescription(selectedCategory.description);
      const selectedParent = categories.find(
        (c) => c.id == selectedCategory.parent,
      );
      if (selectedParent) {
        setParent({ ...selectedParent, label: selectedParent.name });
      } else {
        setParent(null);
      }
    } else {
      setDescription("");
      setParent(null);
      setName("");
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
      <Paper elevation={4} sx={{ p: 2 }}>
        <Typography variant="h5" align="center" sx={{ mb: 3 }}>
          Category Form
        </Typography>
        <Stack spacing={2}>
          <TextField
            onChange={(e) => setName(e.target.value)}
            label="Category name"
            value={name}
            fullWidth
          />
          <TextField
            onChange={(e) => setDescription(e.target.value)}
            label="Category description"
            value={description}
            fullWidth
          />
          <Autocomplete
            options={categories
              .filter((c) => c.id != categoryId)
              .map((c) => ({ ...c, label: c.name }))}
            disabled={categories.length === 0}
            onChange={(_, v) => setParent(v)}
            value={parent}
            renderInput={(params) => (
              <TextField {...params} label="Parent category" />
            )}
          />
        </Stack>
        <Box sx={{ display: "flex", justifyContent: "end", mt: 2 }}>
          <Stack spacing={2} direction="row">
            <Fab
              color="secondary"
              aria-label="EditIcon"
              onClick={(_) =>
                submitHandler("put", `${API_URLS.category}${categoryId}/`)
              }
              disabled={categoryId === undefined}
            >
              <EditIcon />
            </Fab>
            <Fab
              color="primary"
              aria-label="add"
              onClick={(_) => submitHandler("post", API_URLS.category)}
            >
              <AddIcon />
            </Fab>
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}
