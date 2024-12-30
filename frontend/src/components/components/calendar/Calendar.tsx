import { useSearchParams } from "react-router-dom";
import { useDispatch } from "react-redux";
import dayjs from "dayjs";
import React from "react";

import { DateCalendar } from "@mui/x-date-pickers/DateCalendar";

import { setTransactions } from "../../reducers/mainReducer";
import { Methods, APIs, API } from "../../api";

import { TransactionTypeNumber } from "../../pages/transactionsPage/types";

export function Calendar() {
  const [searchParams, setSearchParams] = useSearchParams();
  const dispatch = useDispatch();
  const api = new API();

  React.useEffect(() => {
    let currentDate = searchParams.get("currentDate");
    if (!currentDate) {
      currentDate = dayjs().format("YYYY-MM-DD");
      setSearchParams((prev) => {
        prev.set("currentDate", currentDate as string);
        return prev;
      });
    }
    api.send<TransactionTypeNumber[]>({
      url: APIs.TransactionDateRange,
      method: Methods.post,
      data: { start_date: currentDate, end_date: currentDate },
      onFail: () => dispatch(setTransactions([])),
      onSuccess: (data) => dispatch(setTransactions(data)),
    });
  }, [searchParams]);

  return (
    <DateCalendar
      value={dayjs(searchParams.get("currentDate"), "YYYY-MM-DD")}
      onChange={(newValue) => {
        setSearchParams((prev) => {
          prev.set("currentDate", newValue.format("YYYY-MM-DD"));
          return prev;
        });
      }}
    />
  );
}
