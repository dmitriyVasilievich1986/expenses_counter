import { useDispatch, useSelector } from "react-redux";
import React from "react";

import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { addProducts } from "../../reducers/mainReducer";
import { mainStateType } from "../../reducers/types";
import { ProductTypeDetailed } from "./types";
import { Link } from "../../components/link";
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
