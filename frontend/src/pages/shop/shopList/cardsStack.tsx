import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';

import { Card } from '@components/card';
import { useCategoryStore } from '@store/category';
import { type ShopSimpleType } from '@store/shop';

export function CardsStack(props: { categoryId: number | null; shops: ShopSimpleType[] }) {
  const categories = useCategoryStore((state) => state.categories);
  const category = categories.find((c) => c.id === props.categoryId);

  return (
    <>
      <Divider sx={{ my: 2 }}>{category ? <Chip label={category.name} /> : null}</Divider>
      <Grid container spacing={2}>
        {props.shops.map((shop) => (
          <Grid size={{ xs: 12, sm: 6, md: 4 }} key={shop.id}>
            <Card title={shop.name} description={shop.description} icon={shop.icon} />
          </Grid>
        ))}
      </Grid>
    </>
  );
}
