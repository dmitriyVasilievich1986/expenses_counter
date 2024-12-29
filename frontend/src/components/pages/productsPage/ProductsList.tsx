import { useDispatch, useSelector } from "react-redux";
import React, { useEffect } from "react";

import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Accordion from "@mui/material/Accordion";
import List from "@mui/material/List";

import { CategoryTypeNumber } from "../categoryPage/types";
import { setProducts } from "../../reducers/mainReducer";
import { mainSelectorType } from "../../reducers/types";
import { LinkBox } from "../../components/link";
import { ProductTypeDetailed } from "./types";
import { PagesURLs } from "../../Constants";
import { API, APIs } from "../../api";

function GroupedProducts(props: { products: ProductTypeDetailed[] }) {
  return (
    <List sx={{ pl: 2 }}>
      {props.products.map((p) => (
        <LinkBox key={p.id} to={`${PagesURLs.Product}/${p!.id}`}>
          {p.name}
        </LinkBox>
      ))}
    </List>
  );
}

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

  const categories: { [key in number]: CategoryTypeNumber } = {};
  products.forEach((p) => {
    categories[p.sub_category.id as number] = p.sub_category;
  });

  return (
    <Container sx={{ maxHeight: "75vh", overflowY: "auto" }}>
      <List>
        {Object.values(categories).map((c: CategoryTypeNumber) => (
          <Accordion defaultExpanded key={c.id}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography component="span">{c.name}</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ maxHeight: "300px", overflowY: "auto" }}>
              <GroupedProducts
                products={products.filter((p) => p.sub_category.id === c.id)}
              />
            </AccordionDetails>
          </Accordion>
        ))}
      </List>
    </Container>
  );
}
