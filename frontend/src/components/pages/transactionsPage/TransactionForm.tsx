import { useSearchParams, useParams, useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import dayjs from "dayjs";
import axios from "axios";
import React from "react";

import InputAdornment from "@mui/material/InputAdornment";
import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { PagesURLs, APIResponseType, API_URLS } from "../../Constants";
import { setMessage } from "../../reducers/mainReducer";
import { ShopAddressType } from "../shopsPage/types";
import { CategoryType } from "../categoryPage/types";
import { ProductType } from "../productsPage/types";
import { TransactionType } from "./types";

export function TransactionForm(props: {
  setTransactions: React.Dispatch<
    React.SetStateAction<
      TransactionType<ProductType<number>, ShopAddressType<number>>[]
    >
  >;
  transactions: TransactionType<ProductType<number>, ShopAddressType<number>>[];
  products: ProductType<CategoryType<number>>[];
  addresses: ShopAddressType<number>[];
}) {
  const [searchParams, _] = useSearchParams();
  const { transactionId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [selectedTransaction, setSelectedTransaction] =
    React.useState<
      TransactionType<
        ProductType<CategoryType<number>>,
        ShopAddressType<number> | null
      >
    >(null);
  const [address, setAddress] = React.useState<ShopAddressType<number> | null>(
    null,
  );
  const [product, setProduct] = React.useState<ProductType<
    CategoryType<number>
  > | null>(null);
  const [price, setPrice] = React.useState<string>("0");
  const [count, setCount] = React.useState<string>("1");

  const resetState = () => {
    setSelectedTransaction(null);
    setProduct(null);
    setAddress(null);
    setPrice("0");
    setCount("1");
  };

  React.useEffect(() => {
    if (transactionId === undefined) {
      resetState();
      return;
    }
    axios
      .get(`${API_URLS.Transaction}${transactionId}/`)
      .then(
        (
          data: APIResponseType<
            TransactionType<
              ProductType<CategoryType<number>>,
              ShopAddressType<number>
            >
          >,
        ) => {
          setPrice(data.data.price.toString());
          setCount(data.data.count.toString());
          setSelectedTransaction(data.data);
          setProduct(data.data.product);
          setAddress(data.data.address);
        },
      )
      .catch(() => resetState());
  }, [props.transactions, transactionId]);

  const productChangeHandler = (
    _: any,
    value: ProductType<CategoryType<number>>,
  ) => {
    setProduct(value);
    if (!value) return;

    const data = {
      product_id: value.id,
    };
    axios
      .post(API_URLS.ProductPrice, data)
      .then(
        (
          data: APIResponseType<
            TransactionType<ProductType<number>, ShopAddressType<number>>
          >,
        ) => {
          setPrice(String(data.data.price ?? 0));
        },
      );
  };

  const submitHandler = (method: "post" | "put", url: string) => {
    const data = {
      date: dayjs(searchParams.get("currentDate"), "YYYY-MM-DD").format(
        "YYYY-MM-DD",
      ),
      price: parseFloat(price),
      count: parseFloat(count),
      product: product!.id,
      address: address!.id,
    };
    axios({ method, url, data })
      .then(
        (
          data: APIResponseType<
            TransactionType<ProductType<number>, ShopAddressType<number>>
          >,
        ) => {
          if (method === "post") {
            props.setTransactions([...props.transactions, data.data]);
            dispatch(
              setMessage({
                message: "Transaction created",
                severity: "success",
              }),
            );
            navigate(`${PagesURLs.Transaction}/${data.data.id}`);
          } else if (method === "put") {
            const newTransactions = props.transactions.map((t) =>
              t.id === data.data.id ? data.data : t,
            );
            props.setTransactions(newTransactions);
            dispatch(
              setMessage({
                message: "Transaction updated",
                severity: "success",
              }),
            );
          }
        },
      )
      .catch((e) => {
        dispatch(setMessage({ message: e.respose.data, severity: "error" }));
      });
  };

  return (
    <Container maxWidth="lg">
      <Form title="Transaction form">
        <Autocomplete
          getOptionLabel={(option) => option.local_name}
          disabled={props.addresses.length === 0}
          onChange={(_, v) => setAddress(v)}
          options={props.addresses}
          value={address}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Shop address"
              color={
                selectedTransaction !== null &&
                selectedTransaction.address?.id !== address?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedTransaction !== null &&
                selectedTransaction.address?.id !== address?.id
                  ? true
                  : undefined
              }
            />
          )}
        />
        <Autocomplete
          groupBy={(option) => option.sub_category.name}
          getOptionLabel={(option) => option.name}
          disabled={props.products.length === 0}
          onChange={productChangeHandler}
          options={props.products}
          value={product}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Product"
              color={
                selectedTransaction !== null &&
                selectedTransaction.product?.id !== product?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedTransaction !== null &&
                selectedTransaction.product?.id !== product?.id
                  ? true
                  : undefined
              }
            />
          )}
        />
        <FormTextField
          isChanged={
            selectedTransaction !== null &&
            String(selectedTransaction.price) !== price
          }
          startAdornment={<InputAdornment position="start">$</InputAdornment>}
          label="Product price"
          onChange={setPrice}
          value={price}
        />
        <FormTextField
          isChanged={
            selectedTransaction !== null &&
            String(selectedTransaction.count) !== count
          }
          label="Products count"
          onChange={setCount}
          value={count}
        />
        <FormActions
          disabledEdit={selectedTransaction === null}
          submitHandler={submitHandler}
          url={API_URLS.Transaction}
          objectId={transactionId}
        />
      </Form>
    </Container>
  );
}
