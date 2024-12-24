import { useSearchParams, useParams, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import axios from "axios";
import React from "react";

import InputAdornment from "@mui/material/InputAdornment";
import Autocomplete from "@mui/material/Autocomplete";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";

import { FormTextField, FormActions, Form } from "../../components/form";
import { MainReducerType, TransactionType } from "../../reducers/types";
import { updateState } from "../../reducers/mainReducer";
import { API_URLS } from "../../Constants";

import dayjs from "dayjs";

export function TransactionForm() {
  const transactions = useSelector(
    (state: MainReducerType) => state.main.transactions,
  );
  const addresses = useSelector(
    (state: MainReducerType) => state.main.addresses,
  );
  const products = useSelector((state: MainReducerType) => state.main.products);

  const [searchParams, _] = useSearchParams();
  const { transactionId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [selectedTransaction, setSelectedTransaction] = React.useState(null);
  const [product, setProduct] = React.useState(null);
  const [address, setAddress] = React.useState(null);
  const [price, setPrice] = React.useState("0");
  const [count, setCount] = React.useState("1");

  React.useEffect(() => {
    const transaction =
      transactions.find((t) => t.id === parseInt(transactionId)) ?? null;
    setSelectedTransaction(transaction);
    if (transaction === null) {
      setProduct(null);
      setAddress(null);
      setPrice("0");
      setCount("1");
    } else {
      const product =
        products.find((p) => p.id === transaction.product) ?? null;
      setProduct(product ? { ...product, label: product.name } : null);
      const address =
        addresses.find((a) => a.id === transaction.address) ?? null;
      setAddress(address ? { ...address, label: address.local_name } : null);
      setPrice(transaction.price.toString());
      setCount(transaction.count.toString());
    }
  }, [transactions, transactionId]);

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
      .then((data) => {
        if (method === "post") {
          dispatch(
            updateState({
              transactions: [...transactions, data.data as TransactionType],
              message: { message: "Transaction created", severity: "success" },
            }),
          );
          navigate(`/create/transaction/${data.data.id}`);
        } else if (method === "put") {
          const newTransaction = transactions.map((t) =>
            t.id === data.data.id ? data.data : t,
          );
          dispatch(
            updateState({
              transactions: newTransaction,
              message: { message: "Transaction updated", severity: "success" },
            }),
          );
        }
      })
      .catch((e) => {
        updateState({
          message: { message: e.respose.data, severity: "error" },
        });
      });
  };

  return (
    <Container maxWidth="lg">
      <Form title="Transaction form">
        <Autocomplete
          options={addresses.map((a) => ({ ...a, label: a.local_name }))}
          onChange={(_, v) => setAddress(v)}
          disabled={addresses.length === 0}
          value={address}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Shop address"
              color={
                selectedTransaction !== null &&
                selectedTransaction.address !== address?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedTransaction !== null &&
                selectedTransaction.address !== address?.id
                  ? true
                  : undefined
              }
            />
          )}
        />
        <Autocomplete
          options={products.map((p) => ({ ...p, label: p.name }))}
          onChange={(_, v) => setProduct(v)}
          disabled={products.length === 0}
          value={product}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Product"
              color={
                selectedTransaction !== null &&
                selectedTransaction.product !== product?.id
                  ? "warning"
                  : "primary"
              }
              focused={
                selectedTransaction !== null &&
                selectedTransaction.product !== product?.id
                  ? true
                  : undefined
              }
            />
          )}
        />
        <FormTextField
          isChanged={
            selectedTransaction !== null && selectedTransaction.price !== price
          }
          startAdornment={<InputAdornment position="start">$</InputAdornment>}
          label="Product price"
          onChange={setPrice}
          value={price}
        />
        <FormTextField
          isChanged={
            selectedTransaction !== null && selectedTransaction.count !== count
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
