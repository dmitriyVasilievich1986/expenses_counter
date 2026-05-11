import { Box } from '@mui/material';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';

import { SpendingsGroupedByMonth, MostPopularProducts } from './charts';

export function Home() {
  return (
    <Box sx={{ p: 2 }}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 12, lg: 6 }}>
          <Paper sx={{ width: '100%', height: '420px' }} elevation={3}>
            <SpendingsGroupedByMonth />
          </Paper>
        </Grid>
        <Grid size={{ xs: 12, md: 12, lg: 6 }}>
          <Paper sx={{ width: '100%', height: '420px' }} elevation={3}>
            <MostPopularProducts />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
