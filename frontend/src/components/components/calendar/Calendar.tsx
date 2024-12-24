import { DateCalendar } from "@mui/x-date-pickers/DateCalendar";
import { useSearchParams } from "react-router-dom";
import dayjs from "dayjs";
import React from "react";

export function Calendar() {
  const [searchParams, setSearchParams] = useSearchParams();

  React.useEffect(() => {
    const currentDate = searchParams.get("currentDate");
    if (!currentDate) {
      setSearchParams((prev) => {
        prev.set("currentDate", dayjs().format("YYYY-MM-DD").toString());
        return prev;
      });
    }
  }, [searchParams]);

  return (
    <DateCalendar
      value={dayjs(searchParams.get("currentDate"), "YYYY-MM-DD")}
      onChange={(newValue) => {
        setSearchParams((prev) => {
          prev.set("currentDate", newValue.format("YYYY-MM-DD").toString());
          return prev;
        });
      }}
    />
  );
}
