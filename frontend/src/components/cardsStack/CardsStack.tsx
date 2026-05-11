/**
 * Renders a category-labeled section with a responsive grid of selectable cards.
 */

import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';
import { useMemo } from 'react';

import { Card } from '@components/card';
import { useCategoryStore } from '@store/category';

import { type ItemType } from './types';

/**
 * Render a divider with an optional category chip and a grid of cards for each item.
 *
 * @param {object} props - Component props.
 * @param {number | null} props.categoryId - Category used for the section chip label; chip hidden when null.
 * @param {ItemType[]} props.items - Items to render as cards.
 * @param {(item: ItemType) => void} props.onClick - Handler invoked when a card is activated.
 * @returns {JSX.Element} Section with divider and card grid.
 */
export function CardsStack(props: {
  categoryId: number | null;
  items: ItemType[];
  onClick: (item: ItemType) => void;
}) {
  const categories = useCategoryStore((state) => state.categories);

  const category = useMemo(
    () => categories?.find((c) => c.id === props.categoryId),
    [categories, props.categoryId]
  );

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
              onClick={() => props.onClick(item)}
            />
          </Grid>
        ))}
      </Grid>
    </>
  );
}
