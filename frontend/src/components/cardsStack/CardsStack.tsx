import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';

import { Card } from '@components/card';
import { useCategoryStore } from '@store/category';
import { type ItemType } from './types';

export function CardsStack(props: {
  categoryId: number | null;
  items: ItemType[];
  onClick: () => void;
}) {
  const categories = useCategoryStore((state) => state.categories);

  const category = categories?.find((c) => c.id === props.categoryId);

  return (
    <>
      <Divider sx={{ my: 2 }}>{category ? <Chip label={category.name} /> : null}</Divider>
      <Grid container spacing={2}>
        {props.items.map((item) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={item.id}>
            <Card
              title={item.name}
              description={item.description}
              icon={item.icon}
              onClick={props.onClick}
            />
          </Grid>
        ))}
      </Grid>
    </>
  );
}
