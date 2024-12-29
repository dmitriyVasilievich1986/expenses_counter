import { useDispatch, useSelector } from "react-redux";
import axios from "axios";
import React from "react";

import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { PagesURLs, APIResponseType, API_URLS } from "../../Constants";
import { setIsLoading, addProducts } from "../../reducers/mainReducer";
import { mainStateType } from "../../reducers/types";
import { ProductTypeDetailed } from "./types";
import { Link } from "../../components/link";

export function ProductsList() {
  const products = useSelector(
    (state: { main: mainStateType }) => state.main.products,
  );
  const dispatch = useDispatch();

  React.useEffect(() => {
    if (products.length === 0) {
      dispatch(setIsLoading(true));
      axios
        .get(API_URLS.Product)
        .then((data: APIResponseType<ProductTypeDetailed[]>) => {
          dispatch(addProducts(data.data));
        })
        .finally(() => dispatch(setIsLoading(false)));
    }
  }, [products]);

  return (
    <List sx={{ pl: 2 }}>
      {products.map((p) => (
        <Box sx={{ my: 2 }}>
          <Link
            key={p.id}
            className="secondary"
            to={`${PagesURLs.Product}/${p!.id}`}
          >
            {p.name}
          </Link>
        </Box>
      ))}
    </List>
  );
}
