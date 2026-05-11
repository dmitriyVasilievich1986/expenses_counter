import Box from '@mui/material/Box';
import dayjs from 'dayjs';
import _ from 'lodash';
import { useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router';

import { useTransactionStore } from '@store/transaction';

import { TransactionsStack } from './TransactionsStack';

export function RightSide() {
  const { transactions } = useTransactionStore();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const currentDate = useMemo(() => {
    const dateParam = searchParams.get('date');
    return dateParam ? dayjs(dateParam) : dayjs();
  }, [searchParams]);

  const transactionsByAddress = _.groupBy(
    (transactions ?? []).filter(
      (transaction) => transaction.date === currentDate.format('YYYY-MM-DD')
    ),
    (transaction) => transaction.addressId
  );

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        overflowY: 'auto',
        maxHeight: 'calc(100vh - 64px)',
      }}
    >
      <Box sx={{ width: '90%', height: 'fit-content' }}>
        {Object.keys(transactionsByAddress).map((addressId) => (
          <TransactionsStack
            key={addressId}
            items={transactionsByAddress[addressId]}
            onClick={() => navigate(`/transaction/${addressId}?${searchParams.toString()}`)}
          />
        ))}
        <Box sx={{ height: '1rem' }} />
      </Box>
    </Box>
  );
}
