import { useDispatch, useSelector } from "react-redux";
import { useNavigate, useParams } from "react-router";
import React, { useEffect } from "react";
import axios from "axios";

import { addCategories, setIsLoading } from "../../reducers/mainReducer";
import { APIResponseType, API_URLS, PagesURLs } from "../../Constants";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import { mainStateType } from "../../reducers/types";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { CategoryTypeNumber } from "./types";

function CategoriesList(props: {
  categories: CategoryTypeNumber[];
  parent: number | null;
}) {
  const { categoryId } = useParams();
  let navigate = useNavigate();

  const filteredCategories = props.categories.filter(
    (c) => c.parent === props.parent,
  );

  if (filteredCategories.length == 0) {
    return null;
  }
  return (
    <List sx={{ pl: 2 }}>
      {filteredCategories.map((c) => (
        <Box key={c.id}>
          <ListItemButton
            onClick={(_) => navigate(`${PagesURLs.Category}/${c.id}`)}
            sx={
              categoryId !== undefined && c.id === parseInt(categoryId)
                ? { backgroundColor: "#bbdefb" }
                : {}
            }
          >
            <ListItemText primary={c.name} />
          </ListItemButton>
          <CategoriesList
            parent={c.id as number}
            categories={props.categories}
          />
        </Box>
      ))}
    </List>
  );
}

export function CategoriesListContainer() {
  const dispatch = useDispatch();

  const categories = useSelector(
    (state: { main: mainStateType }) => state.main.categories,
  );

  useEffect(() => {
    if (categories.length === 0) {
      dispatch(setIsLoading(true));
      axios
        .get(API_URLS.Category)
        .then((data: APIResponseType<CategoryTypeNumber[]>) => {
          dispatch(addCategories(data.data));
        })
        .finally(() => dispatch(setIsLoading(false)));
    }
  }, [categories]);

  return <CategoriesList categories={categories} parent={null} />;
}
