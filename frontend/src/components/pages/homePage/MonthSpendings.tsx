import { useSearchParams } from "react-router-dom";
import React, { useEffect, useState } from "react";
import dayjs from "dayjs";

import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import List from "@mui/material/List";

import { LinkBox } from "../../components/link";
import { Methods, APIs, API } from "../../api";
import { roundToTwo } from "../../support";

import { MonthSpendingsResponseType, MonthSpendingsType } from "./types";

export function MonthSpendings() {
  const [searchParams] = useSearchParams();
  const api = new API();

  const [spendings, setSpendings] = useState<MonthSpendingsType[]>([]);

  useEffect(() => {
    const currentDate = searchParams.get("currentDate");
    if (!currentDate) return;
    api.send<MonthSpendingsResponseType>({
      url: APIs.TransactionMonthSpendings,
      method: Methods.post,
      data: { date: currentDate },
      onSuccess: setSpendings,
    });
  }, [searchParams]);

  return (
    <Container>
      <Typography variant="h6" sx={{ m: 0 }} textAlign="center">
        Spendings for the month:
      </Typography>
      <List>
        {spendings.map((spending) => (
          <LinkBox
            key={spending.date}
            to="/"
            params={{ currentDate: spending.date }}
          >
            <Typography variant="subtitle1" sx={{ m: 0 }}>
              {dayjs(spending.date, "YYYY-MM-DD").format("dddd, MMMM D, YYYY")}
            </Typography>
            <Typography variant="caption" sx={{ m: 0 }}>
              {roundToTwo(spending.summary)}€
            </Typography>
          </LinkBox>
        ))}
      </List>
      <Typography variant="h6" sx={{ m: 0 }} textAlign="center">
        Summary: {roundToTwo(spendings.reduce((a, b) => a + b.summary, 0))}€
      </Typography>
    </Container>
  );
}
