import Box from '@mui/material/Box';
import _ from 'lodash';
import { useNavigate } from 'react-router';

import { useTransactionStore } from '@store/transaction';

import { TransactionsStack } from './TransactionsStack';

export function RightSide() {
  const { transactions, currentDate } = useTransactionStore();
  const navigate = useNavigate();

  const transactionsByAddress = _.groupBy(
    (transactions ?? []).filter(
      (transaction) => transaction.date === currentDate.format('YYYY-MM-DD')
    ),
    (transaction) => transaction.addressId
  );

  return (
    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
      <Box sx={{ width: '90%' }}>
        {Object.keys(transactionsByAddress).map((addressId) => (
          <TransactionsStack
            key={addressId}
            categoryId={addressId ? parseInt(addressId) : null}
            items={transactionsByAddress[addressId]}
            onClick={() => navigate(`/transaction/${addressId}`)}
          />
        ))}
      </Box>
    </Box>
  );
}
