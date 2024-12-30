import { APIResponseType } from "../../api/types";

export type MonthSpendingsType = {
  date: string;
  summary: number;
};

export type MonthSpendingsResponseType = APIResponseType<MonthSpendingsType[]>;
