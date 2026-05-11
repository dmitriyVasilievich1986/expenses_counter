import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';
import _ from 'lodash';
import { useNavigate, useSearchParams } from 'react-router';

import { Card } from '@components/card';
import { useTransactionStore } from '@store/transaction';
import type { TransactionType } from '@store/transaction';

export function TransactionsStack(props: { items: TransactionType[]; onClick: () => void }) {
  const { currentTransaction } = useTransactionStore();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const address = props.items[0].address;
  const totalMoney = _.sumBy(props.items, (item) => item.price * item.count).toFixed(2);

  return (
    <>
      <Divider sx={{ my: 2 }}>
        <Chip label={`${address.localName} [${totalMoney}€]`} />
      </Divider>
      <Grid container spacing={2}>
        {props.items.map((item) => (
          <Grid size={{ md: 6, lg: 12, sm: 12 }} key={item.id}>
            <Card
              title={item.product.name}
              isSelected={currentTransaction?.id === item.id}
              description={`${item.count} * ${item.price}€ = ${(item.price * item.count).toFixed(2)}€`}
              onClick={() => navigate(`/transaction/${item.id}?${searchParams.toString()}`)}
            />
          </Grid>
        ))}
      </Grid>
    </>
  );
}
