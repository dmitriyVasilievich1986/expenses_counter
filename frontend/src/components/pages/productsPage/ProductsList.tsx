import { useDispatch, useSelector } from "react-redux";
import React from "react";

import List from "@mui/material/List";

import { addProducts } from "../../reducers/mainReducer";
import { mainStateType } from "../../reducers/types";
import { LinkBox } from "../../components/link";
import { ProductTypeDetailed } from "./types";
import { PagesURLs } from "../../Constants";
import { API, APIs } from "../../api";

export function ProductsList() {
  const products = useSelector(
    (state: { main: mainStateType }) => state.main.products,
  );
  const dispatch = useDispatch();
  const api = new API();

  React.useEffect(() => {
    if (products.length === 0) {
      api.send<ProductTypeDetailed[]>({
        url: APIs.Product,
        onSuccess: (data) => dispatch(addProducts(data)),
      });
    }
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
