/**
 * Home chart: lists the most popular products with compact price history sparklines and links to each product.
 *
 * @module pages/home/charts/MostPopularProducts
 */

import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import { ProductPriceChart } from '@components/productPriceChart';
import { useStatisticsAPIClient, useTransactionAPIClient } from '@services/apiClient';
import type { ProductSimpleType } from '@store/product/types';
import type { TransactionType } from '@store/transaction/types';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

/**
 * Loads the top popular products and their recent transactions, then renders a label-free mini chart per product.
 * Rows navigate to the product detail route on click.
 *
 * @returns Layout with a title and a stack of product rows (chart + name).
 */
export function MostPopularProducts() {
  const navigate = useNavigate();

  const [data, setData] = useState<ProductSimpleType[] | null>(null);
  const [transactions, setTransactions] = useState<TransactionType[] | null>(null);

  const { getMostPopularProducts } = useStatisticsAPIClient();
  const { getTransactions } = useTransactionAPIClient();

  useEffect(() => {
    let cancelled = false;

    const fetchData = async (ids: number[]) => {
      const payload: TransactionType[] = [];
      let total = 1000;
      try {
        while (payload.length < total) {
          const { data, metadata } = await getTransactions(100, payload.length, 'date', 'asc', [
            { column: 'product_id', operator: 'in', value: ids },
          ]);
          payload.push(...data);
          total = metadata.total;
          if (cancelled) break;
        }
      } catch (error) {
        console.error(error);
        setTransactions(payload);
        return;
      }
      setTransactions(payload);
    };

    if (data === null) {
      getMostPopularProducts(5).then((response) => {
        setData(response);
      });
    } else if (transactions === null) {
      const productIds = data.map((item) => item.id);
      void fetchData(productIds);
    }

    return () => {
      cancelled = true;
    };
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
                <ProductPriceChart
                  data={transactions?.filter((t) => t.productId === item.id) ?? null}
                  removeLabels={true}
                />
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
