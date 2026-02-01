import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DateCalendar } from '@mui/x-date-pickers/DateCalendar';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { PickersDay } from '@mui/x-date-pickers/PickersDay';
import dayjs from 'dayjs';
import _ from 'lodash';
import { useEffect, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router';

import { useTransactionAPIClient } from '../../services/apiClient/transaction';
import { useTransactionStore } from '../../store/transaction';

import type { Dayjs } from 'dayjs';

export function LeftSide() {
  const { transactions } = useTransactionStore();
  const { getTransactions } = useTransactionAPIClient();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const currentDate = useMemo(() => {
    const dateParam = searchParams.get('date');
    return dateParam ? dayjs(dateParam) : dayjs();
  }, [searchParams]);

  useEffect(() => {
    if (transactions === null) {
      getTransactions(currentDate);
    }
  }, [currentDate, transactions]);

  const handleMonthChange = (date: Dayjs | null) => {
    if (date) {
      getTransactions(date);
    }
  };

  const handleDateChange = (date: Dayjs | null) => {
    if (date) {
      setSearchParams({ date: date.format('YYYY-MM-DD') });
      navigate(`/transaction?date=${date.format('YYYY-MM-DD')}`);
    }
  };

  const getTransactionsSumByDate = (date: Dayjs) => {
    const sum = _.sumBy(
      (transactions ?? []).filter((t) => t.date === date.format('YYYY-MM-DD')),
      (t) => t.price * t.count
    );
    return sum > 0 ? `${sum.toFixed(2)}€` : null;
  };

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
        onMonthChange={handleMonthChange}
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
