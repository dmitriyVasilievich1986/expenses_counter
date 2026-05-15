import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import { ProductPriceChart } from '@components/productPriceChart';
import { useStatisticsAPIClient } from '@services/apiClient/statistics';
import type { ProductSimpleType } from '@store/product/types';


import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function MostPopularProducts() {
  const [data, setData] = useState<ProductSimpleType[] | null>(null);
  const { getMostPopularProducts } = useStatisticsAPIClient();
  const navigate = useNavigate();

  useEffect(() => {
    if (data === null) {
      getMostPopularProducts(5).then((response) => {
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
            <Box
              key={item.id}
              className={cx('most-popular-products-item')}
              onClick={() => navigate(`/product/${item.id}`)}
            >
              <Box sx={{ width: '200px', height: '50px' }}>
                <ProductPriceChart productId={item.id} removeLabels={true} />
              </Box>
              <Typography align="left" variant="body1" sx={{ mb: 2 }}>
                {item.name}
              </Typography>
            </Box>
          ))}
        </Stack>
      </Box>
    </Box>
  );
}
