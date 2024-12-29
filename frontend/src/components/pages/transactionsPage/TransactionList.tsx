import { useDispatch, useSelector } from "react-redux";
import { useSearchParams } from "react-router-dom";
import React, { useEffect, useState } from "react";
import dayjs from "dayjs";

import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { setTransactions } from "../../reducers/mainReducer";
import { Params, LinkBox } from "../../components/link";
import { Methods, APIs, API } from "../../api";
import { PagesURLs } from "../../Constants";

import { mainStateType } from "../../reducers/types";
import { TransactionTypeNumber } from "./types";

function roundToTwo(num: number) {
  return Math.round(num * 100) / 100;
}

function Transaction(props: {
  transaction: TransactionTypeNumber;
  changeDate?: boolean;
}) {
  return (
    <LinkBox
      to={`${PagesURLs.Transaction}/${props.transaction.id}`}
      smallPadding
      params={
        new Params({
          address: String(props.transaction.address.id),
          currentDate: props.changeDate
            ? dayjs(props.transaction.date).format("YYYY-MM-DD")
            : undefined,
        })
      }
    >
      <Typography variant="subtitle1" sx={{ m: 0 }}>
        {props.transaction.product.name}
      </Typography>
      <Typography variant="caption" sx={{ m: 0 }}>
        {roundToTwo(props.transaction.price)}$ X{" "}
        {roundToTwo(props.transaction.count)}
      </Typography>
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
        Todays transactions:
      </Typography>
      <List sx={{ pl: 2 }}>
        {transactions.map((t) => (
          <Transaction transaction={t} key={t.id} />
        ))}
      </List>
      <Typography variant="h6" align="center" sx={{ mt: 4 }}>
        Summary:{" "}
        {roundToTwo(
          transactions.reduce((acc, t) => acc + t.price * t.count, 0),
        )}
      </Typography>
    </Box>
  );
}

export function PopularProductsList() {
  const [transactions, setTransactions] = useState<TransactionTypeNumber[]>([]);
  const [searchParams] = useSearchParams();
  const api = new API();

  useEffect(() => {
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
