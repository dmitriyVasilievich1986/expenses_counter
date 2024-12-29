import { useSearchParams } from "react-router-dom";
import axios from "axios";
import dayjs from "dayjs";
import React from "react";

import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import Box from "@mui/material/Box";

import { PagesURLs, APIResponseType, API_URLS } from "../../Constants";
import { Params, Link } from "../../components/link";
import { TransactionTypeNumber } from "./types";

function Transaction(props: {
  transaction: TransactionTypeNumber;
  changeDate?: boolean;
}) {
  return (
    <Box sx={{ my: 2 }}>
      <Link
        className="secondary"
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
      </Link>
    </Box>
  );
}

export function TransactionList(props: {
  transactions: TransactionTypeNumber[];
  setTransactions: React.Dispatch<
    React.SetStateAction<TransactionTypeNumber[]>
  >;
}) {
  if (props.transactions.length === 0) return null;
  return (
    <List sx={{ pl: 2 }}>
      {props.transactions.map((t) => (
        <Transaction transaction={t} key={t.id} />
      ))}
    </List>
  );
}

export function PopularProductsList() {
  const [transactions, setTransactions] = React.useState<
    TransactionTypeNumber[]
  >([]);
  const [searchParams] = useSearchParams();

  React.useEffect(() => {
    const address = searchParams.get("address");
    if (!address) {
      setTransactions([]);
      return;
    }
    axios
      .post(API_URLS.ProductPopular, { address })
      .then((data: APIResponseType<TransactionTypeNumber[]>) => {
        setTransactions(data.data);
      })
      .catch(() => setTransactions([]));
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
