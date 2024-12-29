import { useSearchParams, useParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import React, { useState, useEffect } from "react";

import InputAdornment from "@mui/material/InputAdornment";
import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { useNavigateWithParams } from "../../components/link";
import { Methods, APIs, API } from "../../api";
import { PagesURLs } from "../../Constants";
import {
  updateTransaction,
  addTransactions,
  setAddresses,
  setProducts,
} from "../../reducers/mainReducer";

import { ShopAddressType, ShopAddressTypeNumber } from "../shopsPage/types";
import { TransactionTypeNumber, TransactionTypeDetailed } from "./types";
import { ProductTypeDetailed } from "../productsPage/types";
import { mainStateType } from "../../reducers/types";

export function TransactionForm() {
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
  const api = new API();

  const [selectedTransaction, setSelectedTransaction] =
    useState<TransactionTypeDetailed | null>(null);
  const [address, setAddress] = useState<ShopAddressType<number> | null>(null);
  const [product, setProduct] = useState<ProductTypeDetailed | null>(null);
  const [price, setPrice] = useState<string>("0");
  const [count, setCount] = useState<string>("1");

  const resetState = (data?: TransactionTypeDetailed) => {
    setPrice(data?.price ? String(data?.price) : "0");
    setCount(data?.count ? String(data?.count) : "1");
    setSelectedTransaction(data ?? null);
    setProduct(data?.product ?? null);
    setAddress(data?.address ?? null);
  };

  const getCurrentData = () => {
    api.send<TransactionTypeDetailed>({
      url: `${APIs.Transaction}${transactionId}/`,
      onSuccess: resetState,
      onFail: resetState,
    });
  };

  useEffect(() => {
    if (transactionId === undefined) resetState();
    else getCurrentData();
  }, [transactionId]);

  const productChangeHandler = (_: any, value: ProductTypeDetailed | null) => {
    setProduct(value);
    if (!value) return;

    api.send<TransactionTypeNumber>({
      url: APIs.ProductPrice,
      method: Methods.post,
      data: { product_id: value.id },
      onSuccess: (data) => {
        setPrice(String(data.price ?? 0));
      },
    });
  };

  const submitHandler = (method: Methods.post | Methods.put, url: string) => {
    const data = {
      date: searchParams.get("currentDate"),
      price: parseFloat(price),
      count: parseFloat(count),
      product: product!.id,
      address: address!.id,
    };
    const messages = {
      [Methods.post]: "Transaction created",
      [Methods.put]: "Transaction updated",
    };
    api.send<TransactionTypeNumber>({
      url,
      method,
      data,
      successMessage: { message: messages[method] },
      onSuccess: (data) => {
        if (method === Methods.post) {
          dispatch(addTransactions([data]));
          navigate(`${PagesURLs.Transaction}/${data.id}`);
        } else {
          dispatch(updateTransaction(data));
          resetState();
        }
      },
    });
  };

  const loadProducts = () => {
    if (products.length !== 0 || isLoading) return;
    api.send<ProductTypeDetailed[]>({
      url: APIs.Product,
      onSuccess: (data) => dispatch(setProducts(data)),
    });
  };

  const loadAddresses = () => {
    if (addresses.length !== 0 || isLoading) return;
    api.send<ShopAddressTypeNumber[]>({
      url: APIs.Address,
      onSuccess: (data) => dispatch(setAddresses(data)),
    });
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
          objectId={transactionId}
          url={APIs.Transaction}
        />
      </Form>
    </Container>
  );
}
