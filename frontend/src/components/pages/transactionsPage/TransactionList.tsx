import { useDispatch, useSelector } from "react-redux";
import { useSearchParams } from "react-router-dom";
import React, { useEffect, useState } from "react";
import dayjs from "dayjs";

import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { setTransactions } from "../../reducers/mainReducer";
import { Params, LinkBox } from "../../components/link";
import { mainStateType } from "../../reducers/types";
import { TransactionTypeNumber } from "./types";
import { Methods, APIs, API } from "../../api";
import { PagesURLs } from "../../Constants";

function Transaction(props: {
  transaction: TransactionTypeNumber;
  changeDate?: boolean;
}) {
  return (
    <LinkBox
      to={`${PagesURLs.Transaction}/${props.transaction.id}`}
      params={
        new Params({
          address: String(props.transaction.address.id),
          currentDate: props.changeDate
            ? dayjs(props.transaction.date).format("YYYY-MM-DD")
            : undefined,
        })
      }
    >
      {props.transaction.product.name}:{" "}
      {props.transaction.price * props.transaction.count}
    </LinkBox>
  );
}

export function TransactionList() {
  const transactions = useSelector(
    (state: { main: mainStateType }) => state.main.transactions,
  );

  const [searchParams] = useSearchParams();
  const dispatch = useDispatch();
  const api = new API();

  useEffect(() => {
    const currentDate = searchParams.get("currentDate");
    if (!currentDate) {
      dispatch(setTransactions([]));
      return;
    }
    api.send<TransactionTypeNumber[]>({
      url: APIs.TransactionDateRange,
      method: Methods.post,
      data: { start_date: currentDate, end_date: currentDate },
      onFail: () => dispatch(setTransactions([])),
      onSuccess: (data) => dispatch(setTransactions(data)),
    });
  }, [searchParams]);

  if (transactions.length === 0) return null;
  return (
    <Box>
      <Typography variant="h6" align="center">
        Todays trnasactions:
      </Typography>
      <List sx={{ pl: 2 }}>
        {transactions.map((t) => (
          <Transaction transaction={t} key={t.id} />
        ))}
      </List>
      <Typography variant="h6" align="center" sx={{ mt: 4 }}>
        Summary:{" "}
        {Math.round(
          transactions.reduce((acc, t) => acc + t.price * t.count, 0) * 100,
        ) / 100}
      </Typography>
    </Box>
  );
}

export function PopularProductsList() {
  const [transactions, setTransactions] = useState<TransactionTypeNumber[]>([]);
  const [searchParams] = useSearchParams();
  const api = new API();

  React.useEffect(() => {
    const address = searchParams.get("address");
    if (!address) {
      setTransactions([]);
      return;
    }
    api.send<TransactionTypeNumber[]>({
      url: APIs.ProductPopular,
      method: Methods.post,
      data: { address },
      onFail: () => setTransactions([]),
      onSuccess: setTransactions,
    });
  }, [searchParams]);

  if (transactions.length === 0) return null;
  return (
    <Box>
      <Typography variant="h6" align="center">
        Popular Products:
      </Typography>
      <List sx={{ pl: 2 }}>
        {transactions.map((t) => (
          <Transaction transaction={t} key={t.id} />
        ))}
      </List>
    </Box>
  );
}
