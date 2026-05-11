import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import { Card } from '@components/card';
import { useStatisticsAPIClient } from '@services/apiClient/statistics';
import type { ProductSimpleType } from '@store/product/types';

export function MostPopularProducts() {
  const [data, setData] = useState<ProductSimpleType[] | null>(null);
  const { getMostPopularProducts } = useStatisticsAPIClient();
  const navigate = useNavigate();

  useEffect(() => {
    if (data === null) {
      getMostPopularProducts(6).then((response) => {
        setData(response);
      });
    }
  }, [data]);

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignContent: 'center',
        alignItems: 'center',
        width: '100%',
        height: '100%',
      }}
    >
      <Box sx={{ px: 2, flex: 1, height: 'fit-content' }}>
        <Typography align="center" variant="h6" sx={{ mb: 2 }}>
          Most Popular Products:
        </Typography>
        <Stack spacing={2} sx={{ width: '100%' }}>
          {data?.map((item) => (
            <Card
              key={item.id}
              title={item.name}
              description={item.description}
              onClick={() => navigate(`/product/${item.id}`)}
            />
          ))}
        </Stack>
      </Box>
    </Box>
  );
}
