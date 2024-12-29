import { useSearchParams, useParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import dayjs from "dayjs";
import axios from "axios";
import React from "react";

import InputAdornment from "@mui/material/InputAdornment";
import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import {
  addAddresses,
  setIsLoading,
  addProducts,
  setMessage,
} from "../../reducers/mainReducer";
import { ShopAddressType, ShopAddressTypeNumber } from "../shopsPage/types";
import { FormTextField, FormActions, Form } from "../../components/form";
import { TransactionTypeNumber, TransactionTypeDetailed } from "./types";
import { PagesURLs, APIResponseType, API_URLS } from "../../Constants";
import { useNavigateWithParams } from "../../components/link";
import { UrlParamsType } from "../../components/link/types";
import { ProductTypeDetailed } from "../productsPage/types";
import { mainStateType } from "../../reducers/types";

export function TransactionForm(props: {
  setTransactions: React.Dispatch<
    React.SetStateAction<TransactionTypeNumber[]>
  >;
}) {
  const isLoading = useSelector(
    (state: { main: mainStateType }) => state.main.isLoading,
  );
  const addresses = useSelector(
    (state: { main: mainStateType }) => state.main.addresses,
  );
  const products = useSelector(
    (state: { main: mainStateType }) => state.main.products,
  );

  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigateWithParams();
  const { transactionId } = useParams();
  const dispatch = useDispatch();

  const [selectedTransaction, setSelectedTransaction] =
    React.useState<TransactionTypeDetailed | null>(null);
  const [address, setAddress] = React.useState<ShopAddressType<number> | null>(
    null,
  );
  const [product, setProduct] = React.useState<ProductTypeDetailed | null>(
    null,
  );
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
      .then((data: APIResponseType<TransactionTypeDetailed>) => {
        setPrice(data.data.price.toString());
        setCount(data.data.count.toString());
        setSelectedTransaction(data.data);
        setProduct(data.data.product);
        setAddress(data.data.address);
      })
      .catch(() => resetState());
  }, [transactionId]);

  const productChangeHandler = (_: any, value: ProductTypeDetailed | null) => {
    setProduct(value);
    if (!value) return;

    const data = {
      product_id: value.id,
    };
    axios
      .post(API_URLS.ProductPrice, data)
      .then((data: APIResponseType<TransactionTypeNumber>) => {
        setPrice(String(data.data.price ?? 0));
      });
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
      .then((data: APIResponseType<TransactionTypeNumber>) => {
        if (method === "post") {
          props.setTransactions((prev) => [...prev, data.data]);
          dispatch(setMessage({ message: "Transaction created" }));
          const newParams: UrlParamsType = {
            address: String(data.data.address.id),
            currentDate: dayjs(data.data.date).format("YYYY-MM-DD"),
          };
          navigate(`${PagesURLs.Transaction}/${data.data.id}`, newParams);
        } else if (method === "put") {
          props.setTransactions((prev) =>
            prev.map((t) => (t.id === data.data.id ? data.data : t)),
          );
          dispatch(setMessage({ message: "Transaction updated" }));
        }
      })
      .catch((e) => {
        console.log(e);
        dispatch(setMessage({ message: "Error", severity: "error" }));
      });
  };

  const loadProducts = () => {
    if (products.length !== 0 || isLoading) return;
    dispatch(setIsLoading(true));
    axios
      .get(API_URLS.Product)
      .then((data: APIResponseType<ProductTypeDetailed[]>) => {
        dispatch(addProducts(data.data));
      })
      .finally(() => dispatch(setIsLoading(false)));
  };

  const loadAddresses = () => {
    if (addresses.length !== 0 || isLoading) return;
    dispatch(setIsLoading(true));
    axios
      .get(API_URLS.Address)
      .then((data: APIResponseType<ShopAddressTypeNumber[]>) => {
        dispatch(addAddresses(data.data));
      })
      .finally(() => dispatch(setIsLoading(false)));
  };

  const updateAddress = (_: any, v: ShopAddressTypeNumber | null) => {
    setAddress(v);
    setSearchParams((prev) => {
      if (v === null) prev.delete("address");
      else prev.set("address", String(v.id));
      return prev;
    });
  };

  return (
    <Container maxWidth="lg">
      <Form title="Transaction form">
        <Autocomplete
          getOptionLabel={(option) => option.local_name}
          getOptionKey={(option) => option.id as number}
          onChange={updateAddress}
          onOpen={loadAddresses}
          options={addresses}
          loading={isLoading}
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
          getOptionKey={(option) => option.id as number}
          getOptionLabel={(option) => option.name}
          onChange={productChangeHandler}
          onOpen={loadProducts}
          loading={isLoading}
          options={products}
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
