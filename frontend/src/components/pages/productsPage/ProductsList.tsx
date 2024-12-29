import { useDispatch, useSelector } from "react-redux";
import React, { useEffect } from "react";

import List from "@mui/material/List";

import { setProducts } from "../../reducers/mainReducer";
import { mainSelectorType } from "../../reducers/types";
import { LinkBox } from "../../components/link";
import { ProductTypeDetailed } from "./types";
import { PagesURLs } from "../../Constants";
import { API, APIs } from "../../api";

export function ProductsList() {
  const products = useSelector(
    (state: mainSelectorType) => state.main.products,
  );
  const dispatch = useDispatch();
  const api = new API();

  useEffect(() => {
    if (products.length !== 0) return;
    api.send<ProductTypeDetailed[]>({
      url: APIs.Product,
      onSuccess: (data) => dispatch(setProducts(data)),
    });
  }, [products]);

  return (
    <List sx={{ pl: 2 }}>
      {products.map((p) => (
        <LinkBox key={p.id} to={`${PagesURLs.Product}/${p!.id}`}>
          {p.name}
        </LinkBox>
      ))}
    </List>
  );
}
