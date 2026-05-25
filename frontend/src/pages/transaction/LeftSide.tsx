/**
 * Transaction calendar column: month-scoped fetch into the transaction store, selected day in the URL (`date` query),
 * and per-day spend totals under each `PickersDay`.
 *
 * @module pages/transaction/LeftSide
 */

import Box from '@mui/material/Box';
import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DateCalendar } from '@mui/x-date-pickers/DateCalendar';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { PickersDay } from '@mui/x-date-pickers/PickersDay';
import dayjs from 'dayjs';
import _ from 'lodash';
import { useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router';

import type { TransactionType } from '@store/transaction';

import { useTransactionAPIClient } from '../../services/apiClient/transaction';
import { useTransactionStore } from '../../store/transaction';

import type { Dayjs } from 'dayjs';

/**
 * Renders MUI `DateCalendar` wired to `?date=YYYY-MM-DD`, loads all transactions for the visible month into the store,
 * and shows line totals (`price * count`) under days that have activity.
 *
 * @returns The localized date calendar and custom day slots.
 */
export function LeftSide() {
  const [searchParams, setSearchParams] = useSearchParams();

  const { transactions, setTransactions } = useTransactionStore();

  const { getTransactions } = useTransactionAPIClient();

  const currentDate = useMemo<Dayjs>(() => {
    const paramsDate = searchParams.get('date');
    const dayjsDate = dayjs(paramsDate);
    if (!paramsDate || !dayjsDate.isValid()) return dayjs();
    return dayjsDate;
  }, [searchParams]);

  /** Fetches every page of transactions between the month's start and end (inclusive) and replaces the store list. */
  const handleMonthChange = async (date: Dayjs | null) => {
    if (date === null) return;

    const startDate = date.startOf('month').format('YYYY-MM-DD');
    const endDate = date.endOf('month').format('YYYY-MM-DD');
    let total = 1000;
    const payload: TransactionType[] = [];
    const filters = [
      { column: 'date', operator: 'ge', value: startDate },
      { column: 'date', operator: 'le', value: endDate },
    ];

    while (payload.length < total) {
      try {
        const { data, metadata } = await getTransactions(
          100,
          payload.length,
          undefined,
          undefined,
          filters
        );
        payload.push(...data);
        total = metadata.total;
      } catch (error) {
        console.error(error);
        break;
      }
    }

    setTransactions(payload);
  };

  /** Updates the `date` search param and navigates to the same route with the new day selected. */
  const handleDateChange = (date: Dayjs | null) => {
    const paramsDate = searchParams.get('date');
    const paramsDayjsDate = dayjs(paramsDate);
    if (date) {
      setSearchParams((previous) => {
        previous.set('date', date.format('YYYY-MM-DD'));
        return previous;
      });
    }
    if (!paramsDate || !paramsDayjsDate.isValid() || paramsDayjsDate.month() !== date?.month()) {
      handleMonthChange(date);
    }
  };

  useEffect(() => {
    if (!searchParams.get('date')) {
      handleDateChange(currentDate);
    }
  }, [searchParams]);

  useEffect(() => {
    return () => {
      setTransactions(null);
    };
  }, []);

  /** Sums `price * count` for transactions matching the calendar day; returns a formatted euro string or null when zero. */
  const getTransactionsSumByDate = (date: Dayjs) => {
    const sum = _.sumBy(
      (transactions ?? []).filter((t) => t.date === date.format('YYYY-MM-DD')),
      (t) => t.price * t.count
    );
    return sum > 0 ? `${sum.toFixed(2)}€` : null;
  };

  if (transactions === null) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          mt: 1,
        }}
      >
        <Stack direction="column" spacing={1}>
          <Skeleton variant="rectangular" sx={{ width: '300px', height: '50px' }} />
          <Skeleton variant="rectangular" sx={{ width: '300px', height: '290px' }} />
        </Stack>
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DateCalendar
        sx={{
          height: 'max-content',
          maxHeight: 'max-content',
          '& .MuiDayCalendar-slideTransition': {
            minHeight: '290px',
          },
        }}
        value={currentDate}
        onChange={handleDateChange}
        onMonthChange={handleDateChange}
        slots={{
          day: (props) => (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <PickersDay {...props} />
              <Typography
                gutterBottom
                variant="caption"
                sx={{ fontSize: '0.6rem', color: 'text.secondary' }}
              >
                {getTransactionsSumByDate(props.day)}
              </Typography>
            </Box>
          ),
        }}
      />
    </LocalizationProvider>
  );
}
