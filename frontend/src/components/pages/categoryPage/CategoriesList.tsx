import { useDispatch, useSelector } from "react-redux";
import React, { useEffect } from "react";

import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { addCategories } from "../../reducers/mainReducer";
import { LinkBox } from "../../components/link";
import { PagesURLs } from "../../Constants";
import { APIs, API } from "../../api";

import { mainStateType } from "../../reducers/types";
import { CategoryTypeNumber } from "./types";

function CategoriesList(props: {
  categories: CategoryTypeNumber[];
  parent: number | null;
}) {
  const filteredCategories = props.categories.filter(
    (c) => c.parent === props.parent,
  );

  if (filteredCategories.length == 0) return null;
  return (
    <List sx={{ pl: 2 }}>
      {filteredCategories.map((c) => (
        <Box key={c.id}>
          <LinkBox to={`${PagesURLs.Category}/${c.id}`}>{c.name}</LinkBox>
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
  const api = new API();

  const categories = useSelector(
    (state: { main: mainStateType }) => state.main.categories,
  );

  useEffect(() => {
    if (categories.length === 0) {
      api.send<CategoryTypeNumber[]>({
        url: APIs.Category,
        onSuccess: (data) => dispatch(addCategories(data)),
      });
    }
  }, [categories]);

  return <CategoriesList categories={categories} parent={null} />;
}
